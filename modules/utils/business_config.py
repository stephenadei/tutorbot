"""
Load business config from S3 (synced from @stephen/business-config).
"""
import json
import os

import boto3

_BUCKET = os.environ.get('DATALAKE_BUCKET', 'tutoring-datalake-711210709750')
_KEY = 'tutoring/config/business-config.json'
_config = None


def get_config():
    """Load and cache business config from S3."""
    global _config
    if _config is None:
        try:
            s3 = boto3.client('s3')
            obj = s3.get_object(Bucket=_BUCKET, Key=_KEY)
            _config = json.loads(obj['Body'].read())
        except Exception:
            fallback = os.path.join(os.path.dirname(__file__), '..', '..', 'business-config.json')
            if os.path.exists(fallback):
                with open(fallback) as f:
                    _config = json.load(f)
            else:
                raise
    return _config


def phone():
    return get_config()['contact']['phone']['primary']['display']

def phone_raw():
    return get_config()['contact']['phone']['primary']['number']

def email():
    return get_config()['contact']['email']['primary']

def whatsapp_url():
    return get_config()['contact']['whatsappUrls']['primary']
