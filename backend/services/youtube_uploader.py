import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

# Required Scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "youtube_token.json")

def find_client_config() -> dict:
    """
    Sucht nach den Google Client Secrets:
    1. Umgebungsvariable GOOGLE_CLIENT_SECRET_JSON
    2. Umgebungsvariablen GOOGLE_CLIENT_ID & GOOGLE_CLIENT_SECRET
    3. client_secret.json an mehreren möglichen Pfaden (backend, root, current dir)
    """
    # 1. Direct JSON Env Var (ideal für Render.com Deployment)
    env_json = os.getenv("GOOGLE_CLIENT_SECRET_JSON")
    if env_json and env_json.strip():
        try:
            return json.loads(env_json.strip())
        except Exception as e:
            print(f"Warnung: GOOGLE_CLIENT_SECRET_JSON ist kein gültiges JSON: {e}")

    # 2. Key Pair Env Vars
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if client_id and client_secret:
        return {
            "web": {
                "client_id": client_id.strip(),
                "client_secret": client_secret.strip(),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
            }
        }

    # 3. Dateipfade durchsuchen
    search_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "client_secret.json"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "client_secret.json"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "client_secret.json"),
        os.path.join(os.getcwd(), "client_secret.json"),
        os.path.join(os.getcwd(), "backend", "client_secret.json")
    ]

    for p in search_paths:
        norm = os.path.normpath(p)
        if os.path.exists(norm):
            try:
                with open(norm, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "web" in data or "installed" in data:
                        return data
            except Exception as e:
                print(f"Fehler beim Lesen von {norm}: {e}")

    return None

def save_client_secret_json(json_content: str):
    """
    Speichert eine hochgeladene oder eingefügte client_secret.json im Backend-Ordner.
    """
    data = json.loads(json_content.strip())
    target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "client_secret.json")
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return True

def get_auth_url(redirect_uri: str):
    """
    Erstellt die Google OAuth Login URL für YouTube.
    """
    config = find_client_config()
    if not config:
        return None, "CLIENT_SECRETS_FILE_MISSING"

    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            config, scopes=SCOPES
        )
        flow.redirect_uri = redirect_uri

        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        return authorization_url, state
    except Exception as e:
        print(f"Fehler bei get_auth_url: {e}")
        return None, str(e)

def fetch_token_from_code(code: str, redirect_uri: str):
    """
    Tauscht den OAuth-Code gegen Zugangsdaten ein und speichert sie in youtube_token.json.
    """
    config = find_client_config()
    if not config:
        raise Exception("Google Client Configuration nicht gefunden.")

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        config, scopes=SCOPES
    )
    flow.redirect_uri = redirect_uri
    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Speichern der Tokens
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(credentials.to_json())

    return True

def is_authenticated() -> bool:
    """
    Prüft ob gültige YouTube Tokens existieren.
    """
    if not os.path.exists(TOKEN_FILE):
        return False
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        return bool(creds and (creds.valid or creds.refresh_token))
    except:
        return False

def get_authenticated_service():
    """
    Lädt die Credentials und initialisiert den YouTube API Service.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Fehler beim Laden von youtube_token.json: {e}")

    if not creds:
        return None

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
            except Exception as re:
                print(f"Fehler bei YouTube Token Refresh: {re}")
                return None
        else:
            return None

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def upload_short(file_path: str, title: str, description: str, privacy_status: str = "public"):
    """
    Lädt ein Video als YouTube Short hoch.
    Sichtbarkeit: public, private, oder unlisted
    """
    youtube = get_authenticated_service()
    if not youtube:
        raise Exception("Nicht authentifiziert bei YouTube")

    if "#Shorts" not in description and "#shorts" not in description:
        description += "\n\n#Shorts #MIMAROS"

    body = {
        "snippet": {
            "title": title[:100],
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
            print(f"YouTube Upload Progress: {int(status.progress() * 100)}%")

    print(f"YouTube Upload abgeschlossen! Video ID: {response.get('id')}")
    return response
