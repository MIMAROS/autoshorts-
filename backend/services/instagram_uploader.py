import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "instagram_token.json")
APP_ID = os.getenv("INSTAGRAM_APP_ID", "")
APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET", "")
SCOPES = "instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement"

def get_auth_url(redirect_uri: str):
    """
    Erstellt die Meta / Instagram OAuth Login URL.
    """
    app_id = os.getenv("INSTAGRAM_APP_ID", APP_ID)
    if not app_id:
        return None, "INSTAGRAM_APP_ID_MISSING"
        
    url = f"https://www.facebook.com/v19.0/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&scope={SCOPES}&response_type=code"
    return url, None

def fetch_token_from_code(code: str, redirect_uri: str):
    """
    Tauscht den Auth-Code gegen ein langlebiges Token und ermittelt die verknüpfte Instagram Business Account ID.
    """
    app_id = os.getenv("INSTAGRAM_APP_ID", APP_ID)
    app_secret = os.getenv("INSTAGRAM_APP_SECRET", APP_SECRET)
    if not app_id or not app_secret:
        raise ValueError("INSTAGRAM_APP_ID oder INSTAGRAM_APP_SECRET fehlt in der .env")
        
    # 1. Short-Lived Access Token anfordern
    token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
    res = requests.get(token_url, params={
        "client_id": app_id,
        "client_secret": app_secret,
        "redirect_uri": redirect_uri,
        "code": code
    })
    data = res.json()
    if "access_token" not in data:
        raise Exception(f"Fehler beim Abrufen des Short-Lived Tokens: {data}")
    short_token = data["access_token"]
    
    # 2. Long-Lived Token anfordern (60 Tage gültig)
    ll_res = requests.get("https://graph.facebook.com/v19.0/oauth/access_token", params={
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token
    })
    ll_data = ll_res.json()
    long_token = ll_data.get("access_token", short_token)
    
    # 3. Instagram Business Account ID finden über verknüpfte Facebook-Seiten
    pages_res = requests.get("https://graph.facebook.com/v19.0/me/accounts", params={
        "access_token": long_token
    })
    pages_data = pages_res.json()
    
    ig_user_id = None
    page_access_token = long_token
    
    if "data" in pages_data and len(pages_data["data"]) > 0:
        for page in pages_data["data"]:
            p_id = page.get("id")
            p_token = page.get("access_token", long_token)
            ig_res = requests.get(f"https://graph.facebook.com/v19.0/{p_id}", params={
                "fields": "instagram_business_account,name",
                "access_token": p_token
            })
            ig_data = ig_res.json()
            if "instagram_business_account" in ig_data:
                ig_user_id = ig_data["instagram_business_account"]["id"]
                page_access_token = p_token
                break
                
    token_payload = {
        "access_token": long_token,
        "page_access_token": page_access_token,
        "ig_user_id": ig_user_id,
        "created_at": time.time()
    }
    
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(token_payload, f, indent=4)
        
    return token_payload

def save_manual_token(access_token: str, ig_user_id: str):
    """
    Speichert ein manuell generiertes Token (z.B. aus dem Meta Graph API Explorer).
    """
    token_payload = {
        "access_token": access_token.strip(),
        "page_access_token": access_token.strip(),
        "ig_user_id": ig_user_id.strip(),
        "created_at": time.time()
    }
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(token_payload, f, indent=4)
    return token_payload

def is_authenticated() -> bool:
    """
    Prüft ob gültige Instagram-Tokens hinterlegt sind.
    """
    if not os.path.exists(TOKEN_FILE):
        return False
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return bool(data.get("access_token") and data.get("ig_user_id"))
    except:
        return False

def disconnect():
    """
    Löscht die gespeicherten Instagram-Tokens.
    """
    if os.path.exists(TOKEN_FILE):
        try:
            os.remove(TOKEN_FILE)
            return True
        except:
            pass
    return False

def upload_reel(video_url: str, caption: str) -> dict:
    """
    Lädt ein Video als Instagram Reel über die Meta Graph API hoch.
    Benötigt eine öffentlich erreichbare URL des Videos (z.B. Supabase Storage oder Render URL).
    """
    if not is_authenticated():
        raise Exception("Instagram ist nicht authentifiziert. Bitte verbinde deinen Account.")
        
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        token_data = json.load(f)
        
    token = token_data.get("page_access_token") or token_data.get("access_token")
    ig_user_id = token_data.get("ig_user_id")
    
    if not token or not ig_user_id:
        raise Exception("Ungültige Instagram Anmeldedaten in instagram_token.json")

    # Schritt 1: Media-Container erstellen
    create_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": True,
        "access_token": token
    }
    
    print(f"Erstelle Instagram Reels Container für Video: {video_url}...")
    res = requests.post(create_url, data=payload)
    container_data = res.json()
    
    if "id" not in container_data:
        raise Exception(f"Fehler beim Erstellen des Instagram Reels Containers: {container_data}")
        
    container_id = container_data["id"]
    print(f"Instagram Container ID: {container_id}. Warte auf Video-Verarbeitung bei Meta...")
    
    # Schritt 2: Status pollen bis Meta das Video fertig verarbeitet hat
    status_url = f"https://graph.facebook.com/v19.0/{container_id}"
    max_retries = 30 # Bis zu 2.5 Minuten warten
    status = "IN_PROGRESS"
    
    for _ in range(max_retries):
        time.sleep(5)
        status_res = requests.get(status_url, params={"fields": "status_code", "access_token": token})
        status_json = status_res.json()
        status = status_json.get("status_code", "IN_PROGRESS")
        print(f"Instagram Verarbeitungsstatus: {status}")
        
        if status == "FINISHED":
            break
        elif status in ["ERROR", "EXPIRED"]:
            raise Exception(f"Instagram Video-Verarbeitung fehlgeschlagen: {status_json}")
            
    if status != "FINISHED":
        raise Exception(f"Timeout bei der Instagram Video-Verarbeitung (Status: {status})")

    # Schritt 3: Reel veröffentlichen
    publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
    pub_res = requests.post(publish_url, data={
        "creation_id": container_id,
        "access_token": token
    })
    pub_data = pub_res.json()
    
    if "id" not in pub_data:
        raise Exception(f"Fehler bei der Veröffentlichung des Reels: {pub_data}")
        
    print(f"Instagram Reel erfolgreich veröffentlicht! Media-ID: {pub_data['id']}")
    return pub_data
