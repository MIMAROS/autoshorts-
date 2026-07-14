import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "client_secret.json")
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "youtube_token.json")

def get_auth_url(redirect_uri: str):
    """
    Returns the Google OAuth login URL.
    """
    if not os.path.exists(CLIENT_SECRETS_FILE):
        return None, "CLIENT_SECRETS_FILE_MISSING"

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES
    )
    flow.redirect_uri = redirect_uri

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    return authorization_url, state

def fetch_token_from_code(code: str, redirect_uri: str):
    """
    Exchanges the OAuth code for credentials and saves them to TOKEN_FILE.
    """
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES
    )
    flow.redirect_uri = redirect_uri
    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Speichern der Tokens
    with open(TOKEN_FILE, "w") as f:
        f.write(credentials.to_json())

    return True

def is_authenticated():
    """
    Prüft ob gültige YouTube Tokens existieren.
    """
    return os.path.exists(TOKEN_FILE)

def get_authenticated_service():
    """
    Lädt die Credentials und baut den YouTube API Service.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        else:
            return None

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def upload_short(file_path: str, title: str, description: str, privacy_status: str = "private"):
    """
    Lädt ein Video als YouTube Short hoch.
    Sichtbarkeit: public, private, oder unlisted
    """
    youtube = get_authenticated_service()
    if not youtube:
        raise Exception("Nicht authentifiziert bei YouTube")

    # WICHTIG: Um als Short erkannt zu werden, muss '#Shorts' im Titel oder in der Beschreibung sein.
    if "#Shorts" not in description and "#shorts" not in description:
        description += "\n\n#Shorts"

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "22" # People & Blogs
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=googleapiclient.http.MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )

    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    return response
