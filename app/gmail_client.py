import os
import base64

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

def _header(headers, name):
    """Gmail returns headers as a list of {name, value} pairs."""
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _decode(data):
    """Gmail encodes bodies as URL-safe base64, sometimes missing padding."""
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")


def _extract_body(payload):
    """Emails are nested 'parts'. Walk the tree and return the first plain-text part."""
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return _decode(payload["body"]["data"])
    for part in payload.get("parts", []) or []:
        text = _extract_body(part)
        if text:
            return text
    return ""


def fetch_recent_messages(service, max_results=25, newer_than_days=30):
    """Return recent emails as simple dicts: id, sender, subject, date, body."""
    listing = service.users().messages().list(
        userId="me", q=f"newer_than:{newer_than_days}d", maxResults=max_results
    ).execute()

    messages = []
    for item in listing.get("messages", []):
        msg = service.users().messages().get(
            userId="me", id=item["id"], format="full"
        ).execute()
        headers = msg["payload"].get("headers", [])
        messages.append({
            "gmail_id": msg["id"],
            "sender": _header(headers, "From"),
            "subject": _header(headers, "Subject"),
            "date": _header(headers, "Date"),
            # Some emails are HTML-only; fall back to Gmail's short preview.
            "body": _extract_body(msg["payload"]) or msg.get("snippet", ""),
        })
    return messages