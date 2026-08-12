import os
import subprocess
import tempfile
from openai import OpenAI

def transcribe_audio(video_path: str, video_lang: str = "auto", subtitle_lang: str = "auto") -> dict:
    """
    Transkribiert Audio über die Cloud-basierte OpenAI Whisper API (whisper-1).
    Extrem ressourcenschonend (< 50MB RAM) & blitzschnell (Kein lokales PyTorch/Model im RAM).
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Datei nicht gefunden: {video_path}")
        
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("WARNUNG: OPENAI_API_KEY ist nicht in den Umgebungsvariablen gesetzt!")
        
    client = OpenAI(api_key=api_key)
    
    print(f"Starte OpenAI Whisper API Transkription für: {video_path}")
    
    # 1. Extrahiere leichtes MP3-Audio per FFmpeg (unter 25MB für die API)
    temp_dir = tempfile.mkdtemp()
    temp_audio = os.path.join(temp_dir, "temp_audio.mp3")
    
    try:
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "libmp3lame", "-ar", "16000", "-ac", "1", "-b:a", "64k",
            temp_audio
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        target_file = temp_audio
    except Exception as e:
        print(f"FFmpeg Audio-Extraktion Hinweis ({e}), nutze Originaldatei.")
        target_file = video_path

    try:
        with open(target_file, "rb") as audio_file:
            kwargs = {
                "model": "whisper-1",
                "file": audio_file,
                "response_format": "verbose_json"
            }
            if video_lang and video_lang != "auto":
                kwargs["language"] = video_lang
                
            response = client.audio.transcriptions.create(**kwargs)
            
        # Parse Response (Pydantic / dict kompatibel)
        if isinstance(response, dict):
            full_text = response.get("text", "")
            raw_segments = response.get("segments", [])
        else:
            full_text = getattr(response, "text", "") or ""
            raw_segments = getattr(response, "segments", []) or []
        
        segments = []
        for seg in raw_segments:
            if isinstance(seg, dict):
                start = float(seg.get("start", 0.0))
                end = float(seg.get("end", 0.0))
                text = str(seg.get("text", "")).strip()
            else:
                start = float(getattr(seg, "start", 0.0))
                end = float(getattr(seg, "end", 0.0))
                text = str(getattr(seg, "text", "")).strip()
            segments.append({"start": start, "end": end, "text": text})
            
        print(f"Whisper API Transkription erfolgreich: {len(segments)} Segmente erzeugt.")
        return {
            "text": full_text,
            "segments": segments
        }
    except Exception as err:
        print(f"Fehler bei OpenAI Whisper API Transkription: {err}")
        raise err
    finally:
        if os.path.exists(temp_audio):
            try: os.remove(temp_audio)
            except: pass
        if os.path.exists(temp_dir):
            try: os.rmdir(temp_dir)
            except: pass
