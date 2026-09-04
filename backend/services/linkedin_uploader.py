import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "linkedin_token.json")
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
SCOPES = "openid,profile,w_member_social"

def get_auth_url(redirect_uri: str):
    """
    Erstellt die LinkedIn OAuth 2.0 Autorisierungs-URL.
    """
    client_id = os.getenv("LINKEDIN_CLIENT_ID", CLIENT_ID)
    if not client_id:
        return None, "LINKEDIN_CLIENT_ID_MISSING"

    url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={SCOPES}"
        f"&state=mimaros_linkedin_auth"
    )
    return url, None

def fetch_token_from_code(code: str, redirect_uri: str):
    """
    Tauscht den Auth-Code gegen ein LinkedIn Access-Token ein und ermittelt die User-URN.
    """
    client_id = os.getenv("LINKEDIN_CLIENT_ID", CLIENT_ID)
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", CLIENT_SECRET)
    if not client_id or not client_secret:
        raise ValueError("LINKEDIN_CLIENT_ID oder LINKEDIN_CLIENT_SECRET fehlt in der .env")

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    res = requests.post(token_url, data=data, headers=headers)
    token_data = res.json()

    if "access_token" not in token_data:
        raise Exception(f"Fehler beim Abrufen des LinkedIn Tokens: {token_data}")

    access_token = token_data["access_token"]

    # Member Profile / Sub URN abfragen
    user_info_res = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info = user_info_res.json()
    person_urn = f"urn:li:person:{user_info.get('sub', '')}" if user_info.get('sub') else ""
    user_name = user_info.get("name", "LinkedIn User")

    payload = {
        "access_token": access_token,
        "expires_in": token_data.get("expires_in", 5184000), # 60 Tage
        "person_urn": person_urn,
        "user_name": user_name,
        "created_at": time.time()
    }

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)

    return payload

def save_manual_token(access_token: str, person_urn: str = ""):
    """
    Speichert ein manuelles LinkedIn Access-Token.
    """
    if not person_urn.startswith("urn:li:person:") and person_urn:
        person_urn = f"urn:li:person:{person_urn}"

    payload = {
        "access_token": access_token.strip(),
        "person_urn": person_urn.strip(),
        "user_name": "LinkedIn Member",
        "created_at": time.time()
    }
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)
    return payload

def is_authenticated() -> bool:
    """
    Prüft ob gültige LinkedIn Tokens existieren.
    """
    if not os.path.exists(TOKEN_FILE):
        return False
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return bool(data.get("access_token"))
    except:
        return False

def disconnect():
    """
    Löscht gespeicherte LinkedIn Tokens.
    """
    if os.path.exists(TOKEN_FILE):
        try:
            os.remove(TOKEN_FILE)
            return True
        except:
            pass
    return False

def upload_video(file_path_or_url: str, caption: str, title: str = "MIMAROS Video") -> dict:
    """
    Veröffentlicht ein Video auf LinkedIn über die offizielle LinkedIn Posts API.
    """
    if not is_authenticated():
        raise Exception("LinkedIn ist nicht authentifiziert. Bitte verbinde deinen Account.")

    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        token_data = json.load(f)

    access_token = token_data.get("access_token")
    person_urn = token_data.get("person_urn")

    # Falls person_urn nicht vorhanden, live abfragen
    if not person_urn:
        user_info_res = requests.get(
            "https://api.linkedin.com/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        sub = user_info_res.json().get("sub")
        if sub:
            person_urn = f"urn:li:person:{sub}"
            token_data["person_urn"] = person_urn
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                json.dump(token_data, f, indent=4)
        else:
            raise Exception("Konnte LinkedIn Person URN nicht ermitteln.")

    headers_rest = {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": "202401",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    # Schritt 1: Video Upload Initialisieren
    file_size = os.path.getsize(file_path_or_url) if os.path.exists(file_path_or_url) else 5000000
    init_url = "https://api.linkedin.com/rest/videos?action=initializeUpload"
    init_payload = {
        "initializeUploadRequest": {
            "owner": person_urn,
            "fileSizeBytes": file_size,
            "uploadCaptions": False,
            "uploadThumbnail": False
        }
    }

    print(f"Initiiere LinkedIn Video Upload für {person_urn}...")
    res = requests.post(init_url, headers=headers_rest, json=init_payload)
    init_data = res.json()

    if "value" not in init_data:
        # Fallback: Versuche klassischen UGC Assets Flow
        return upload_video_ugc_fallback(file_path_or_url, caption, title, access_token, person_urn)

    video_urn = init_data["value"]["video"]
    upload_instructions = init_data["value"]["uploadInstructions"]

    # Schritt 2: Binäre Video-Chunks hochladen
    with open(file_path_or_url, "rb") as f:
        video_bytes = f.read()

    for instruction in upload_instructions:
        upload_url = instruction["uploadUrl"]
        put_res = requests.put(upload_url, data=video_bytes, headers={"Content-Type": "application/octet-stream"})
        if put_res.status_code not in [200, 201]:
            raise Exception(f"Fehler beim LinkedIn Video Chunk Upload: {put_res.status_code}")

    # Schritt 3: Post auf LinkedIn veröffentlichen
    post_url = "https://api.linkedin.com/rest/posts"
    post_payload = {
        "author": person_urn,
        "commentary": caption,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "content": {
            "media": {
                "title": title[:100],
                "id": video_urn
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }

    post_res = requests.post(post_url, headers=headers_rest, json=post_payload)
    if post_res.status_code in [201, 200]:
        print("LinkedIn Video Post erfolgreich veröffentlicht!")
        return {"status": "success", "video_urn": video_urn}
    else:
        raise Exception(f"Fehler bei LinkedIn Veröffentlichung: {post_res.status_code} - {post_res.text}")

def upload_video_ugc_fallback(file_path: str, caption: str, title: str, access_token: str, person_urn: str):
    """
    Fallback-Methode über die LinkedIn UGC Post API.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    # 1. Register Upload
    register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    reg_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
            "owner": person_urn,
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }
    reg_res = requests.post(register_url, headers=headers, json=reg_payload).json()
    asset = reg_res["value"]["asset"]
    upload_url = reg_res["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]

    # 2. Upload Bytes
    with open(file_path, "rb") as f:
        video_bytes = f.read()
    requests.put(upload_url, data=video_bytes, headers={"Content-Type": "application/octet-stream"})

    # 3. Create UGC Post
    ugc_url = "https://api.linkedin.com/v2/ugcPosts"
    ugc_payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "media": [{
                    "media": asset,
                    "status": "READY",
                    "title": {"text": title[:100]}
                }],
                "shareCommentary": {"text": caption},
                "shareMediaCategory": "VIDEO"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    ugc_res = requests.post(ugc_url, headers=headers, json=ugc_payload)
    if ugc_res.status_code in [200, 201]:
        print("LinkedIn Video erfolgreich via UGC API veröffentlicht!")
        return {"status": "success", "asset": asset}
    else:
        raise Exception(f"Fehler beim Erstellen des LinkedIn UGC Posts: {ugc_res.status_code} - {ugc_res.text}")
