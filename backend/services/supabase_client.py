import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    supabase = None

def upload_file_to_supabase(local_file_path: str, bucket_name: str, remote_file_name: str) -> str:
    """
    Lädt eine lokale Datei zu Supabase Storage hoch und gibt die Public URL zurück.
    Gibt im Fehlerfall (oder wenn Supabase nicht konfiguriert ist) None zurück.
    """
    if not supabase:
        print("Supabase client not initialized.")
        return None
    try:
        with open(local_file_path, "rb") as f:
            res = supabase.storage.from_(bucket_name).upload(
                file=f,
                path=remote_file_name,
                file_options={"content-type": "video/mp4"}
            )
        
        # Public URL holen
        url = supabase.storage.from_(bucket_name).get_public_url(remote_file_name)
        return url
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")
        return None
