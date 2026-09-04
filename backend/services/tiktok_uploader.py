import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tiktok_token.json")
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")
SCOPES = "user.info.basic,video.upload,video.publish"

def get_auth_url(redirect_uri: str):
    """
    Erstellt die TikTok OAuth2 Autorisierungs-URL.
    """
    client_key = os.getenv("TIKTOK_CLIENT_KEY", CLIENT_KEY)
    if not client_key:
        return None, "TIKTOK_CLIENT_KEY_MISSING"
        
    url = (
        f"https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={client_key}"
        f"&scope={SCOPES}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
    )
    return url, None

def fetch_token_from_code(code: str, redirect_uri: str):
    """
    Tauscht den Auth-Code gegen ein Access- und Refresh-Token ein.
    """
    client_key = os.getenv("TIKTOK_CLIENT_KEY", CLIENT_KEY)
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET", CLIENT_SECRET)
    if not client_key or not client_secret:
        raise ValueError("TIKTOK_CLIENT_KEY oder TIKTOK_CLIENT_SECRET fehlt in der .env")
        
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_key": client_key,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }
    
    res = requests.post(url, headers=headers, data=data)
    token_data = res.json()
    
    if "access_token" not in token_data and "data" in token_data:
        token_data = token_data["data"]
        
    if "access_token" not in token_data:
        raise Exception(f"Fehler beim Abrufen des TikTok Tokens: {token_data}")
        
    payload = {
        "access_token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token"),
        "open_id": token_data.get("open_id"),
        "expires_in": token_data.get("expires_in", 86400),
        "created_at": time.time()
    }
    
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)
        
    return payload

def save_manual_token(access_token: str, open_id: str = ""):
    """
    Speichert ein manuell generiertes Token für Testzwecke.
    """
    payload = {
        "access_token": access_token.strip(),
        "open_id": open_id.strip(),
        "created_at": time.time()
    }
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)
    return payload

def is_authenticated() -> bool:
    """
    Prüft ob gültige TikTok-Tokens hinterlegt sind.
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
    Löscht die gespeicherten TikTok-Tokens.
    """
    if os.path.exists(TOKEN_FILE):
        try:
            os.remove(TOKEN_FILE)
            return True
        except:
            pass
    return False

def refresh_token_if_needed():
    """
    Aktualisiert das Access Token falls vorhanden und nötig.
    """
    if not is_authenticated():
        return None
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        client_key = os.getenv("TIKTOK_CLIENT_KEY", CLIENT_KEY)
        client_secret = os.getenv("TIKTOK_CLIENT_SECRET", CLIENT_SECRET)
        refresh_token = data.get("refresh_token")
        
        if not refresh_token or not client_key or not client_secret:
            return data.get("access_token")
            
        url = "https://open.tiktokapis.com/v2/oauth/token/"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = requests.post(url, headers=headers, data={
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        })
        new_data = res.json()
        if "data" in new_data and "access_token" in new_data["data"]:
            data["access_token"] = new_data["data"]["access_token"]
            data["refresh_token"] = new_data["data"].get("refresh_token", refresh_token)
            data["created_at"] = time.time()
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
                
        return data.get("access_token")
    except Exception as e:
        print(f"Hinweis bei TikTok Token Refresh: {e}")
        return None

def upload_video(file_path_or_url: str, title: str, privacy_level: str = "PUBLIC_TO_EVERYONE") -> dict:
    """
    Veröffentlicht ein Video auf TikTok via TikTok Content Posting API.
    Unterstützt sowohl lokale Videodateien als auch direkte öffentliche URLs.
    """
    if not is_authenticated():
        raise Exception("TikTok ist nicht authentifiziert. Bitte verbinde deinen Account.")
        
    access_token = refresh_token_if_needed()
    if not access_token:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            access_token = json.load(f).get("access_token")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }

    # Wenn eine öffentliche URL vorliegt (z.B. Supabase / Cloud)
    if file_path_or_url.startswith("http://") or file_path_or_url.startswith("https://"):
        init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        payload = {
            "post_info": {
                "title": title,
                "privacy_level": privacy_level,
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": file_path_or_url
            }
        }
        
        print(f"Initiiere TikTok Video Upload von URL: {file_path_or_url}...")
        res = requests.post(init_url, headers=headers, json=payload)
        data = res.json()
        
        if "error" in data and data["error"].get("code") != "ok":
            raise Exception(f"Fehler beim TikTok Video Init: {data}")
            
        print(f"TikTok Video Post erfolgreich initiiert: {data}")
        return data
    else:
        # Lokale Datei Direct Chunk Upload
        if not os.path.exists(file_path_or_url):
            raise FileNotFoundError(f"Lokale Datei nicht gefunden: {file_path_or_url}")
            
        file_size = os.path.getsize(file_path_or_url)
        init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        payload = {
            "post_info": {
                "title": title,
                "privacy_level": privacy_level,
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": file_size,
                "total_chunk_count": 1
            }
        }
        
        res = requests.post(init_url, headers=headers, json=payload)
        data = res.json()
        
        if "data" not in data or "upload_url" not in data["data"]:
            raise Exception(f"Fehler beim Abrufen der TikTok Upload-URL: {data}")
            
        upload_url = data["data"]["upload_url"]
        publish_id = data["data"]["publish_id"]
        
        # Binär-Upload der Videodatei
        with open(file_path_or_url, "rb") as f:
            video_bytes = f.read()
            
        put_headers = {
            "Content-Type": "video/mp4",
            "Content-Range": f"bytes 0-{file_size - 1}/{file_size}"
        }
        
        print(f"Lade Video-Bytes zu TikTok hoch (Größe: {file_size} Bytes)...")
        put_res = requests.put(upload_url, headers=put_headers, data=video_bytes)
        
        if put_res.status_code not in [200, 201]:
            raise Exception(f"Fehler beim Hochladen der Video-Bytes zu TikTok: {put_res.status_code} - {put_res.text}")
            
        print(f"TikTok Video erfolgreich hochgeladen! Publish ID: {publish_id}")
        return {"publish_id": publish_id, "status": "success"}
