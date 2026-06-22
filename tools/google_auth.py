import base64
import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send',
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')


def get_credentials():
    creds = None

    # Production: load token directly from env var (no files needed)
    token_b64 = os.getenv('TOKEN_JSON_B64')
    if token_b64:
        token_data = json.loads(base64.b64decode(token_b64).decode())
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    elif os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            if not token_b64 and os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'w') as f:
                    f.write(creds.to_json())
        else:
            # Local dev only — run browser OAuth flow
            if not os.path.exists(CREDENTIALS_FILE):
                raise RuntimeError('credentials.json not found. See SETUP.md.')
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())

    return creds


def get_calendar_service():
    return build('calendar', 'v3', credentials=get_credentials())


def get_gmail_service():
    return build('gmail', 'v1', credentials=get_credentials())
