import os
import requests

CW_URL = os.environ.get("CW_URL", "https://crm.stephenadei.nl")
ACC = os.environ.get("CW_ACCOUNT_ID", "1")
ADMIN_TOKEN = os.environ.get("CW_ADMIN_TOKEN")

if not ADMIN_TOKEN:
    print("❌ CW_ADMIN_TOKEN not set in environment!")
    exit(1)

headers = {
    "api_access_token": ADMIN_TOKEN,
    "Content-Type": "application/json"
}

contacts = []
page = 1
print(f"Fetching contacts from {CW_URL} (account {ACC})...")
while True:
    resp = requests.get(f"{CW_URL}/api/v1/accounts/{ACC}/contacts?page={page}", headers=headers)
    if resp.status_code != 200:
        print(f"❌ Failed to fetch contacts: {resp.status_code} {resp.text}")
        break
    data = resp.json()
    payload = data.get("payload", [])
    if not payload:
        break
    contacts.extend(payload)
    if not data.get("meta", {}).get("has_more"):
        break
    page += 1

print(f"\n{'ID':<8} {'Name':<30} {'Language':<10}")
print("-"*50)
for c in contacts:
    cid = c.get("id", "?")
    name = c.get("name", "")
    attrs = c.get("custom_attributes", {})
    lang = attrs.get("language", None)
    print(f"{cid:<8} {name:<30} {str(lang):<10}")

print(f"\nTotal contacts: {len(contacts)}")