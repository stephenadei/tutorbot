import os
from zoneinfo import ZoneInfo

CW = os.getenv("CW_URL", "https://crm.stephenadei.nl")
ACC = os.getenv("CW_ACC_ID")
TOK = os.getenv("CW_TOKEN")
ADMIN_TOK = os.getenv("CW_ADMIN_TOKEN")
SIG = os.getenv("CW_HMAC_SECRET")

TZ = ZoneInfo("Europe/Amsterdam")
AGE_TTL_DAYS = int(os.getenv("AGE_TTL_DAYS", "365"))

# Export all variables
__all__ = ['CW', 'ACC', 'TOK', 'ADMIN_TOK', 'SIG', 'TZ', 'AGE_TTL_DAYS']
