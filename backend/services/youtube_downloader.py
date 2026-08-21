import yt_dlp
import os

def download_video(url: str, output_path: str = "temp", trim_start: int = None, trim_end: int = None) -> str:
    """
    Lädt ein YouTube Video herunter und speichert es in bestmöglicher Qualität (max 1080p).
    Wenn trim_start und trim_end angegeben sind, wird nur dieser Bereich heruntergeladen.
    Gibt den Dateipfad zum heruntergeladenen Video zurück.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': f'{output_path}/%(id)s.%(ext)s',
        'quiet': False,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'extractor_args': {'youtube': ['player_client=android']}
    }

    if trim_start is not None and trim_end is not None:
        # We need ffmpeg to download specific sections from YouTube.
        # Syntax: *start_time-end_time
        ydl_opts['download_ranges'] = lambda info, ydl: [{'start_time': trim_start, 'end_time': trim_end}]
        ydl_opts['force_keyframes_at_cuts'] = True

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Falls Format zusammengeführt wird, ändert sich ggf. die Extension
            if not os.path.exists(filename):
                # Check for .mkv or other formats if ffmpeg merged them differently
                base, _ = os.path.splitext(filename)
                for ext in ['.mp4', '.mkv', '.webm']:
                    if os.path.exists(base + ext):
                        filename = base + ext
                        break
            return filename
    except Exception as e:
        print(f"Fehler beim Download: {e}")
        raise e

def search_youtube_videos(query: str, max_results: int = 8) -> list:
    """
    Sucht auf YouTube nach Videos basierend auf einem Suchbegriff oder Thema.
    Gibt eine Liste von Video-Metadaten zurück.
    """
    clean_query = (query or "").strip()
    if not clean_query:
        return []
        
    # Prüfe ob direkte URL
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'extractor_args': {'youtube': ['player_client=android']}
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
                    
                # Thumbnail Ermittlung
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
    Unterstützt auch automatischen Such-Fallback, falls ein Suchbegriff statt URL übergeben wird.
    """
    clean_url = (url or "").strip()
    if not clean_url.startswith(('http://', 'https://', 'www.', 'youtube.com', 'youtu.be')):
        # User entered a search term -> Search first video
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'extractor_args': {'youtube': ['player_client=android']}
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
        # Fallback to search
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
