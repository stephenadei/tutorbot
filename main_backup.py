from flask import Flask, request
import os, hmac, hashlib, requests
from datetime import datetime, timedelta

# Import our refactored modules
from tutorbot.config import CW, ACC, TOK, ADMIN_TOK, SIG, TZ, AGE_TTL_DAYS
from tutorbot.bot.translations import TRANSLATIONS, t
from tutorbot.bot.state import conversation_memory
from tutorbot.bot.helpers import is_valid_name, detect_language, now_ams, parse_dt, is_contact_age_valid, is_weekend_now
from tutorbot.bot.api import ok, api, send_text, send_select, set_contact_attrs, set_conv_attrs, add_conv_labels

app = Flask(__name__)

# Global flag to track if setup is done
setup_completed = False

# ---------- Language detection and translation ----------

# ---------- Chatwoot setup and attributes ----------