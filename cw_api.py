"""
Chatwoot API client following best practices
"""
import os
import requests
from typing import Dict, List, Optional, Any

# Configuration
CW_URL = os.environ.get("CW_URL", "https://crm.stephenadei.nl")
ACC = os.environ.get("CW_ACCOUNT_ID", "1")
ADMIN_TOKEN = os.environ.get("CW_ADMIN_TOKEN")
TOKEN = os.environ.get("CW_TOKEN")

if not ADMIN_TOKEN or not TOKEN:
    raise ValueError("CW_ADMIN_TOKEN and CW_TOKEN must be set in environment")

def _admin_headers():
    """Headers for admin API calls"""
    return {
        "api_access_token": ADMIN_TOKEN,
        "Content-Type": "application/json"
    }

def _user_headers():
    """Headers for user API calls"""
    return {
        "api_access_token": ADMIN_TOKEN,  # Use admin token for all API calls
        "Content-Type": "application/json"
    }

class ChatwootAPI:
    """Chatwoot API client with proper error handling"""
    
    @staticmethod
    def search_contact(query: str) -> Optional[Dict]:
        """Search for a contact by phone/email/identifier"""
        url = f"{CW_URL}/api/v1/accounts/{ACC}/contacts/search"
        try:
            response = requests.get(
                url, 
                headers=_admin_headers(), 
                params={"q": query}, 
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            # Return first contact if found
            contacts = data.get("payload", [])
            return contacts[0] if contacts else None
        except Exception as e:
            print(f"❌ Search contact failed: {e}")
            return None
    
    @staticmethod
    def create_contact(inbox_id: int, name: str, phone: str, attrs: Dict = None) -> Optional[Dict]:
        """Create a new contact"""
        url = f"{CW_URL}/api/v1/accounts/{ACC}/contacts"
        payload = {
            "inbox_id": inbox_id,
            "name": name,
            "phone_number": phone
        }
        if attrs:
            payload["custom_attributes"] = attrs
            
        try:
            response = requests.post(url, headers=_admin_headers(), json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Create contact failed: {e}")
            return None
    
    @staticmethod
    def update_contact(contact_id: int, attrs: Dict = None, name: str = None) -> Optional[Dict]:
        """Update contact attributes and/or name"""
        url = f"{CW_URL}/api/v1/accounts/{ACC}/contacts/{contact_id}"
        payload = {}
        if attrs:
            payload["custom_attributes"] = attrs
        if name:
            payload["name"] = name
            
        try:
            response = requests.put(url, headers=_admin_headers(), json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Update contact failed: {e}")
            return None
    
    @staticmethod
    def get_contact(contact_id: int) -> Optional[Dict]:
        """Get contact details including custom attributes"""
        url = f"{CW_URL}/api/v1/accounts/{ACC}/contacts/{contact_id}"
        try:
            response = requests.get(url, headers=_admin_headers(), timeout=10)
            response.raise_for_status()
            data = response.json()
            # Handle both direct response and payload wrapper
            if "payload" in data:
                return data["payload"]
            return data
        except Exception as e:
            print(f"❌ Get contact failed: {e}")
            return None
    
    @staticmethod
    def get_contact_attrs(contact_id: int) -> Dict:
        """Get contact custom attributes"""
        contact = ChatwootAPI.get_contact(contact_id)
        if contact:
            return contact.get("custom_attributes", {})
        return {}
    
    @staticmethod
    def set_contact_attrs(contact_id: int, attrs: Dict) -> bool:
        """Set contact custom attributes (merge with existing)"""
        # First get current attributes
        current = ChatwootAPI.get_contact_attrs(contact_id)
        # Merge with new attributes
        merged = {**current, **attrs}
        # Update contact
        result = ChatwootAPI.update_contact(contact_id, attrs=merged)
        return result is not None
    
    @staticmethod
    def get_conversation(conversation_id: int) -> Optional[Dict]:
        """Get conversation details"""
        url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations/{conversation_id}"
        try:
            response = requests.get(url, headers=_user_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Get conversation failed: {e}")
            return None
    
    @staticmethod
    def get_conv_attrs(conversation_id: int) -> Dict:
        """Get conversation custom attributes"""
        conv = ChatwootAPI.get_conversation(conversation_id)
        if conv:
            return conv.get("custom_attributes", {})
        return {}
    
    @staticmethod
    def set_conv_attrs(conversation_id: int, attrs: Dict) -> bool:
        """Set conversation custom attributes"""
        url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations/{conversation_id}/custom_attributes"
        try:
            response = requests.post(
                url, 
                headers=_user_headers(), 
                json={"custom_attributes": attrs}, 
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Set conversation attributes failed: {e}")
            return False
    
    @staticmethod
    def get_conv_labels(conversation_id: int) -> List[str]:
        """Get conversation labels"""
        url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations/{conversation_id}/labels"
        try:
            response = requests.get(url, headers=_user_headers(), timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("labels", [])
        except Exception as e:
            print(f"❌ Get conversation labels failed: {e}")
            return []
    
    @staticmethod
    def set_conv_labels(conversation_id: int, labels: List[str]) -> bool:
        """Set conversation labels (replaces all existing labels)"""
        url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations/{conversation_id}/labels"
        try:
            response = requests.post(
                url, 
                headers=_user_headers(), 
                json={"labels": labels}, 
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Set conversation labels failed: {e}")
            return False
    
    @staticmethod
    def add_conv_labels(conversation_id: int, new_labels: List[str]) -> bool:
        """Add labels to conversation (merge with existing)"""
        current = ChatwootAPI.get_conv_labels(conversation_id)
        merged = sorted(set(current + new_labels))
        return ChatwootAPI.set_conv_labels(conversation_id, merged)
    
    @staticmethod
    def send_message(conversation_id: int, content: str, content_type: str = "text", 
                    content_attributes: Dict = None, private: bool = False) -> bool:
        """Send a message to a conversation"""
        url = f"{CW_URL}/api/v1/accounts/{ACC}/conversations/{conversation_id}/messages"
        payload = {
            "content": content,
            "content_type": content_type,
            "message_type": "outgoing",
            "private": private
        }
        if content_attributes:
            payload["content_attributes"] = content_attributes
            
        try:
            response = requests.post(url, headers=_user_headers(), json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Send message failed: {e}")
            return False

# Convenience functions for backward compatibility
def get_contact_attrs(contact_id: int) -> Dict:
    """Get contact custom attributes"""
    return ChatwootAPI.get_contact_attrs(contact_id)

def set_contact_attrs(contact_id: int, attrs: Dict) -> bool:
    """Set contact custom attributes"""
    return ChatwootAPI.set_contact_attrs(contact_id, attrs)

def get_conv_attrs(conversation_id: int) -> Dict:
    """Get conversation custom attributes"""
    return ChatwootAPI.get_conv_attrs(conversation_id)

def set_conv_attrs(conversation_id: int, attrs: Dict) -> bool:
    """Set conversation custom attributes"""
    return ChatwootAPI.set_conv_attrs(conversation_id, attrs)

def add_conv_labels(conversation_id: int, labels: List[str]) -> bool:
    """Add labels to conversation"""
    return ChatwootAPI.add_conv_labels(conversation_id, labels)

def send_text(conversation_id: int, text: str) -> bool:
    """Send a text message"""
    return ChatwootAPI.send_message(conversation_id, text, "text") 