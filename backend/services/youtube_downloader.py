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

def get_video_info(url: str) -> dict:
    """
    Gibt Metadaten zu einem YouTube Video zurück, ohne es herunterzuladen.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title", "Unbekannt"),
                "duration": info.get("duration", 0),
                "thumbnail": info.get("thumbnail", "")
            }
    except Exception as e:
        print(f"Fehler beim Abrufen der Video-Info: {e}")
        raise e
