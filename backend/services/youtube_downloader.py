import yt_dlp
import os
import subprocess

def download_video(url: str, output_path: str = "temp", trim_start: int = None, trim_end: int = None) -> str:
    """
    Lädt ein YouTube Video herunter und speichert es in bestmöglicher Qualität (max 1080p).
    Robuste Multi-Client-Strategie (Android, iOS, Web, MWeb) für Cloud- und Lokal-Umgebungen.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
        
    clean_url = (url or "").strip()
    if not clean_url.startswith(('http://', 'https://', 'www.', 'youtube.com', 'youtu.be')):
        search_res = search_youtube_videos(clean_url, max_results=1)
        if search_res:
            clean_url = search_res[0].get("url", clean_url)
            
    # Primary resilient options
    ydl_opts_list = [
        # Strategy 1: Multi-client fallback with best mp4/webm up to 1080p
        {
            'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{output_path}/%(id)s.%(ext)s',
            'quiet': False,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web', 'mweb']
                }
            }
        },
        # Strategy 2: iOS client fallback
        {
            'format': 'best[height<=720]/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{output_path}/%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios']
                }
            }
        }
    ]

    downloaded_file = None
    last_err = None

    for opts in ydl_opts_list:
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(clean_url, download=True)
                fn = ydl.prepare_filename(info)
                
                # Check for merged file extensions
                if not os.path.exists(fn):
                    base, _ = os.path.splitext(fn)
                    for ext in ['.mp4', '.mkv', '.webm', '.ts']:
                        if os.path.exists(base + ext):
                            fn = base + ext
                            break
                            
                if os.path.exists(fn) and os.path.getsize(fn) > 0:
                    downloaded_file = fn
                    break
        except Exception as e:
            print(f"yt-dlp Download-Versuch fehlgeschlagen ({e}). Probiere Fallback-Strategie...")
            last_err = e

    if not downloaded_file or not os.path.exists(downloaded_file):
        raise RuntimeError(f"Konnte YouTube-Video nicht herunterladen: {last_err}")

    # Wenn Trimming definiert ist, schneide das Video jetzt sauber lokal per FFmpeg
    if trim_start is not None and trim_end is not None and trim_end > trim_start:
        trimmed_path = os.path.join(output_path, f"trimmed_{os.path.basename(downloaded_file)}")
        dur = trim_end - trim_start
        try:
            subprocess.run([
                "ffmpeg", "-y",
                "-ss", str(trim_start),
                "-t", str(dur),
                "-i", downloaded_file,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-c:a", "aac",
                trimmed_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(trimmed_path) and os.path.getsize(trimmed_path) > 0:
                try: os.remove(downloaded_file)
                except: pass
                return trimmed_path
        except Exception as te:
            print(f"Fehler beim Trimmen nach Download: {te}. Verwende volles Video.")
            
    return downloaded_file

def search_youtube_videos(query: str, max_results: int = 8) -> list:
    """
    Sucht auf YouTube nach Videos basierend auf einem Suchbegriff oder Thema.
    Gibt eine Liste von Video-Metadaten zurück.
    """
    clean_query = (query or "").strip()
    if not clean_query:
        return []
        
    if clean_query.startswith(('http://', 'https://', 'www.', 'youtube.com', 'youtu.be')):
        search_target = clean_query if clean_query.startswith('http') else f"https://{clean_query}"
    else:
        search_target = f"ytsearch{max_results}:{clean_query}"
        
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'skip_download': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web']
            }
        }
    }
    
    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res = ydl.extract_info(search_target, download=False)
            if not res:
                return []
                
            entries = res.get('entries', [])
            if not entries and res.get('id'):
                entries = [res]
                
            for e in entries:
                if not e:
                    continue
                video_id = e.get('id', '')
                url = e.get('url') or e.get('webpage_url') or f"https://www.youtube.com/watch?v={video_id}"
                if not url.startswith('http') and video_id:
                    url = f"https://www.youtube.com/watch?v={video_id}"
                    
                thumbnails = e.get('thumbnails', [])
                thumb = e.get('thumbnail', '')
                if not thumb and thumbnails:
                    thumb = thumbnails[-1].get('url', '')
                if not thumb and video_id:
                    thumb = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                    
                dur_raw = e.get('duration', 0) or 0
                try:
                    dur_val = float(dur_raw)
                except:
                    dur_val = 0.0
                    
                results.append({
                    'id': video_id,
                    'title': e.get('title', 'YouTube Video'),
                    'url': url,
                    'duration': dur_val,
                    'thumbnail': thumb,
                    'channel': e.get('channel') or e.get('uploader') or 'YouTube Creator',
                    'view_count': e.get('view_count', 0) or 0
                })
        return results
    except Exception as e:
        print(f"Fehler bei YouTube Websuche: {e}")
        return []

def get_video_info(url: str) -> dict:
    """
    Gibt Metadaten zu einem YouTube Video zurück, ohne es herunterzuladen.
    """
    clean_url = (url or "").strip()
    if not clean_url.startswith(('http://', 'https://', 'www.', 'youtube.com', 'youtu.be')):
        search_res = search_youtube_videos(clean_url, max_results=1)
        if search_res:
            first = search_res[0]
            return {
                "title": first.get("title", "Unbekannt"),
                "duration": first.get("duration", 0),
                "thumbnail": first.get("thumbnail", ""),
                "url": first.get("url", clean_url)
            }
            
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web']
            }
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)
            video_id = info.get('id', '')
            thumb = info.get("thumbnail", "")
            if not thumb and video_id:
                thumb = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                
            return {
                "title": info.get("title", "Unbekannt"),
                "duration": info.get("duration", 0),
                "thumbnail": thumb,
                "url": clean_url
            }
    except Exception as e:
        search_res = search_youtube_videos(clean_url, max_results=1)
        if search_res:
            first = search_res[0]
            return {
                "title": first.get("title", "Unbekannt"),
                "duration": first.get("duration", 0),
                "thumbnail": first.get("thumbnail", ""),
                "url": first.get("url", clean_url)
            }
        print(f"Fehler beim Abrufen der Video-Info: {e}")
        raise e
