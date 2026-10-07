import os

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Read-only: the app can look at your mail but can never send, delete,
# or change anything. Ask for the least permission you need.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")  # who the APP is
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")              # what YOU allowed


def _save_token(creds):
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())


def get_credentials():
    """Return valid Google credentials, logging in through the browser if needed."""
    creds = None

    # token.json exists after your first login, so later runs skip the browser.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # Access tokens are short-lived; a refresh token quietly gets a new one.
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_token(creds)
        except RefreshError:
            creds = None  # expired or revoked: fall through to a fresh login

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)  # opens your browser
        _save_token(creds)

    return creds


def get_gmail_service():
    """A ready-to-use Gmail API client."""
    return build("gmail", "v1", credentials=get_credentials())