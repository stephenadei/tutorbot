from __future__ import annotations

import requests
from typing import Dict, Iterable

from modules.utils.cw_api import set_contact_attrs, add_conv_labels, remove_conv_labels
from modules.core.config import CW_URL, CW_ACC_ID, CW_ADMIN_TOKEN


def update_contact_attrs(contact_id: int | str, updates: Dict[str, object],
                         conversation_id: int | str | None = None,
                         note: str | None = None) -> bool:
    """Set multiple contact attributes and optionally append a note to the conversation.

    Returns True if attributes were set without exception.
    """
    try:
        set_contact_attrs(contact_id, updates)
        if conversation_id and note:
            add_conv_note(conversation_id, note)
        return True
    except Exception as exc:
        print(f"❌ Failed to update contact {contact_id} attrs {list(updates.keys())}: {exc}")
        return False


def add_conv_note(conversation_id: int | str, content: str) -> None:
    """Add a note to a Chatwoot conversation (best-effort)."""
    try:
        url = f"{CW_URL}/api/v1/accounts/{CW_ACC_ID}/conversations/{conversation_id}/notes"
        headers = {"api_access_token": CW_ADMIN_TOKEN, "Content-Type": "application/json"}
        requests.post(url, headers=headers, json={"content": content}, timeout=10)
    except Exception as _:
        # best-effort
        pass


def add_labels_safe(conversation_id: int | str, labels: Iterable[str]) -> None:
    try:
        add_conv_labels(conversation_id, list(labels))
    except Exception as _:
        pass


def remove_labels_safe(conversation_id: int | str, labels: Iterable[str]) -> None:
    try:
        remove_conv_labels(conversation_id, list(labels))
    except Exception as _:
        pass


