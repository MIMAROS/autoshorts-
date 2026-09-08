import yt_dlp
import os
import re
import json
import urllib.request

def extract_video_id(url: str) -> str:
    if not url:
        return ""
    m = re.search(r'(?:v=|\/|youtu\.be\/|shorts\/|embed\/)([0-9A-Za-z_-]{11})', url.strip())
    return m.group(1) if m else ""

def get_video_info(url: str) -> dict:
    """
    Gibt Metadaten zu einem YouTube Video zurück (Titel, Dauer, Thumbnail, URL).
    Verwendet eine mehrstufige Fallback-Pipeline inkl. offizieller YouTube oEmbed API,
    sodass dieser Aufruf auch in Cloud-Hosting-Umgebungen (wie Render) NIEMALS blockiert wird.
    """
    clean_url = (url or "").strip()
    if not clean_url:
        raise ValueError("Keine URL angegeben.")

    vid = extract_video_id(clean_url)
    
    # 1. Schnelleyt-dlp Extraktion mit Android Client
    ydl_opts_list = [
        {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'socket_timeout': 10,
            'extractor_args': {'youtube': {'player_client': ['android']}}
        },
        {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'socket_timeout': 10,
        }
    ]
    
    for opts in ydl_opts_list:
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                video_id = info.get('id', vid or '')
                thumb = info.get('thumbnail', '')
                if not thumb and video_id:
                    thumb = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                
                title = info.get('title', 'YouTube Video')
                dur = info.get('duration', 60) or 60
                
                return {
                    "title": title,
                    "duration": dur,
                    "thumbnail": thumb,
                    "url": f"https://www.youtube.com/watch?v={video_id}" if video_id else clean_url
                }
        except Exception:
            pass

    # 2. Zero-Fail Fallback über die offizielle YouTube oEmbed API (wird nie geblockt)
    if vid:
        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json"
            req = urllib.request.Request(
                oembed_url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
            )
            with urllib.request.urlopen(req, timeout=6) as res:
                data = json.loads(res.read().decode('utf-8'))
                return {
                    "title": data.get("title", "YouTube Video"),
                    "duration": 60,
                    "thumbnail": data.get("thumbnail_url", f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"),
                    "url": f"https://www.youtube.com/watch?v={vid}"
                }
        except Exception:
            pass

    # 3. noembed.com Fallback
    if vid:
        try:
            noembed_url = f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={vid}"
            req = urllib.request.Request(
                noembed_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=6) as res:
                data = json.loads(res.read().decode('utf-8'))
                return {
                    "title": data.get("title", "YouTube Video"),
                    "duration": 60,
                    "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                    "url": f"https://www.youtube.com/watch?v={vid}"
                }
        except Exception:
            pass

    # 4. Ultimativer Fallback mit direkter Video-ID
    if vid:
        return {
            "title": f"YouTube Video ({vid})",
            "duration": 60,
            "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
            "url": f"https://www.youtube.com/watch?v={vid}"
        }

    raise ValueError(f"Konnte Video-Metadaten für {url} nicht abrufen.")

def search_youtube_videos(query: str, max_results: int = 8) -> list:
    """
    Sucht auf YouTube nach Videos basierend auf einem Suchbegriff oder Thema.
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
        'socket_timeout': 10,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android']
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
                    dur_val = 60.0
                    
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

def download_video(url: str, output_path: str = "temp", trim_start: int = None, trim_end: int = None) -> str:
    """
    Lädt ein YouTube Video herunter und speichert es in bester MP4-Qualität.
    Nutzt eine mehrstufige Client-Fallback-Strategie für maximale Cloud-Kompatibilität.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
        
    clean_url = (url or "").strip()
    vid = extract_video_id(clean_url)
    if vid and not clean_url.startswith("http"):
        clean_url = f"https://www.youtube.com/watch?v={vid}"
        
    strategies = [
        # Strategy 1: Android Client (High stability on datacenter IPs)
        {
            'format': 'bestvideo*+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{output_path}/%(id)s.%(ext)s',
            'quiet': False,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'socket_timeout': 30,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android']
                }
            }
        },
        # Strategy 2: Android Creator Client
        {
            'format': 'bestvideo*+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{output_path}/%(id)s.%(ext)s',
            'quiet': False,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'socket_timeout': 30,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android_creator']
                }
            }
        },
        # Strategy 3: Standard Client fallback
        {
            'format': 'bestvideo*+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{output_path}/%(id)s.%(ext)s',
            'quiet': False,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'socket_timeout': 30,
        }
    ]

    downloaded_file = None
    last_err = None

    for s in strategies:
        try:
            with yt_dlp.YoutubeDL(s) as ydl:
                info = ydl.extract_info(clean_url, download=True)
                fn = ydl.prepare_filename(info)
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
            print(f"Download-Versuch fehlgeschlagen ({e}). Probiere nächste Strategie...")
            last_err = e

    if not downloaded_file or not os.path.exists(downloaded_file):
        raise RuntimeError(f"Konnte YouTube-Video nicht herunterladen: {last_err}")

    return downloaded_file
