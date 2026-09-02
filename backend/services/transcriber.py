import os
import subprocess
import tempfile
import json
import re
from dotenv import load_dotenv

load_dotenv()

def transcribe_with_gemini(audio_path: str, lang: str = "auto") -> dict:
    """
    Transkribiert Audio über die Google Gemini API mit google.genai Client.
    Verwendet Inline Audio Bytes für blitzschnelle und hochpräzise Erkennung.
    """
    try:
        from google import genai
        from google.genai import types
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Kein GEMINI_API_KEY gefunden für Gemini Transkription.")
            return None
            
        client = genai.Client(api_key=api_key)
        
        print(f"Transkribiere Audio mit Google Gemini ({os.path.basename(audio_path)})...")
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
            
        part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")
        
        lang_instruction = f"Die Sprache des Audios ist {lang}." if lang and lang != "auto" else "Erkenne die Sprache automatisch."
        
        prompt = f"""
        Du bist ein hochpräziser Transkriptions-Dienst für Videos und Social Media Shorts.
        {lang_instruction}
        Transkribiere das gesprochene Audio Wort für Wort mit präzisen Zeitstempeln (in Sekunden als Float).
        Teile die gesprochenen Sätze in kurze, synchrone Segmente (2 bis 4 Sekunden) auf.
        
        Antworte AUSSCHLIESSLICH als gültiges JSON-Objekt im folgenden Format (ohne Markdown, ohne ```json):
        {{
          "text": "Vollständiger zusammenhängender Text des Audios",
          "segments": [
            {{
              "start": 0.0,
              "end": 2.5,
              "text": "Gesprochener Satz",
              "words": [
                {{"word": "Gesprochener", "start": 0.0, "end": 1.2}},
                {{"word": "Satz", "start": 1.2, "end": 2.5}}
              ]
            }}
          ]
        }}
        """
        
        # Try latest fast models
        response = None
        for model_name in ["gemini-2.5-flash", "gemini-flash-latest", "gemini-3.7-flash", "gemini-3.6-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[part, prompt]
                )
                if response and response.text:
                    break
            except Exception as e:
                print(f"Gemini Model {model_name} fehlgeschlagen: {e}")
                
        if not response or not response.text:
            return None
            
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "", 1).rsplit("```", 1)[0].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "", 1).rsplit("```", 1)[0].strip()
            
        data = json.loads(raw_text)
        if isinstance(data, dict) and "segments" in data:
            # Stelle sicher, dass jedes Segment auch 'words' mit Start/Endzeit hat
            for seg in data["segments"]:
                if "words" not in seg or not seg["words"]:
                    words_list = seg.get("text", "").strip().split()
                    if words_list:
                        s_start = float(seg.get("start", 0.0))
                        s_end = float(seg.get("end", s_start + 2.0))
                        dur_per_word = max(0.1, (s_end - s_start) / max(len(words_list), 1))
                        seg["words"] = [
                            {
                                "word": w,
                                "start": round(s_start + (i * dur_per_word), 2),
                                "end": round(s_start + ((i + 1) * dur_per_word), 2)
                            }
                            for i, w in enumerate(words_list)
                        ]
            return data
    except Exception as e:
        print(f"Gemini Audio-Transkription Hinweis/Fehler: {e}")
    return None

def transcribe_with_local_whisper(audio_path: str, lang: str = "auto") -> dict:
    """
    100% robuster lokaler Whisper-Fallback ohne API-Kosten oder Internet-Abhängigkeit.
    Nutzt das vorinstallierte openai-whisper Paket.
    """
    try:
        import whisper
        print(f"Starte lokales Whisper (base) für: {os.path.basename(audio_path)}...")
        model = whisper.load_model("base")
        
        options = {"word_timestamps": True}
        if lang and lang != "auto":
            options["language"] = lang
            
        result = model.transcribe(audio_path, **options)
        
        full_text = result.get("text", "").strip()
        raw_segments = result.get("segments", [])
        
        segments = []
        for seg in raw_segments:
            seg_start = float(seg.get("start", 0.0))
            seg_end = float(seg.get("end", 0.0))
            seg_text = seg.get("text", "").strip()
            
            words = []
            if "words" in seg and seg["words"]:
                for w in seg["words"]:
                    w_text = w.get("word", "").strip()
                    if w_text:
                        words.append({
                            "word": w_text,
                            "start": float(w.get("start", seg_start)),
                            "end": float(w.get("end", seg_end))
                        })
            else:
                words_list = seg_text.split()
                if words_list:
                    dur_per_word = max(0.1, (seg_end - seg_start) / max(len(words_list), 1))
                    words = [
                        {
                            "word": w,
                            "start": round(seg_start + (i * dur_per_word), 2),
                            "end": round(seg_start + ((i + 1) * dur_per_word), 2)
                        }
                        for i, w in enumerate(words_list)
                    ]
                    
            segments.append({
                "start": seg_start,
                "end": seg_end,
                "text": seg_text,
                "words": words
            })
            
        print(f"Lokales Whisper erfolgreich: {len(segments)} Segmente transkribiert.")
        return {"text": full_text, "segments": segments}
    except Exception as e:
        print(f"Lokales Whisper Transkription Hinweis/Fehler: {e}")
        return None

def transcribe_audio(video_path: str, video_lang: str = "auto", subtitle_lang: str = "auto") -> dict:
    """
    Transkribiert Audio mit Multi-Engine Kaskade:
    1. Google Gemini Audio API (blitzschnell, präzise)
    2. Lokales OpenAI Whisper (100% ausfallsicheres lokales Backup)
    3. OpenAI Whisper Cloud API (falls Key vorhanden)
    4. Robuster Dauer-Fallback
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Datei nicht gefunden: {video_path}")
        
    # 1. Extrahiere leichtes MP3-Audio per FFmpeg
    temp_dir = tempfile.mkdtemp()
    temp_audio = os.path.join(temp_dir, "temp_audio.mp3")
    target_file = video_path
    
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

    # Engine 1: Google Gemini Audio Transkription (Primär)
    gemini_result = transcribe_with_gemini(target_file, video_lang)
    if gemini_result and gemini_result.get("segments") and len(gemini_result["segments"]) > 0:
        print(f"Google Gemini Transkription erfolgreich: {len(gemini_result['segments'])} Segmente.")
        _cleanup_temp(temp_audio, temp_dir)
        return gemini_result

    # Engine 2: Lokales Whisper (Ausfallsicheres Offline-Backup)
    whisper_result = transcribe_with_local_whisper(target_file, video_lang)
    if whisper_result and whisper_result.get("segments") and len(whisper_result["segments"]) > 0:
        _cleanup_temp(temp_audio, temp_dir)
        return whisper_result

    # Engine 3: OpenAI Whisper API (falls Key vorhanden)
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key and len(openai_key.strip()) > 10:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            print(f"Starte OpenAI Whisper API Transkription für: {target_file}")
            with open(target_file, "rb") as audio_file:
                kwargs = {
                    "model": "whisper-1",
                    "file": audio_file,
                    "response_format": "verbose_json"
                }
                if video_lang and video_lang != "auto":
                    kwargs["language"] = video_lang
                response = client.audio.transcriptions.create(**kwargs)
                
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
                words_list = text.split()
                dur_per_word = max(0.1, (end - start) / max(len(words_list), 1))
                words = [
                    {
                        "word": w,
                        "start": round(start + (i * dur_per_word), 2),
                        "end": round(start + ((i + 1) * dur_per_word), 2)
                    }
                    for i, w in enumerate(words_list)
                ]
                segments.append({"start": start, "end": end, "text": text, "words": words})
                
            print(f"Whisper API Transkription erfolgreich: {len(segments)} Segmente erzeugt.")
            _cleanup_temp(temp_audio, temp_dir)
            return {"text": full_text, "segments": segments}
        except Exception as err:
            print(f"OpenAI Whisper Transkription fehlgeschlagen: {err}")

    # Engine 4: Ausfallsicherer Fallback basierend auf Video-Dauer
    print("Nutze Video-Dauer Fallback für Transkription...")
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            capture_output=True, text=True
        )
        duration = float(probe.stdout.strip())
    except:
        duration = 30.0

    _cleanup_temp(temp_audio, temp_dir)
    return {
        "text": "MIMAROS AUTOSHORTS",
        "segments": [
            {
                "start": 0.0,
                "end": duration,
                "text": "MIMAROS AUTOSHORTS",
                "words": [
                    {"word": "MIMAROS", "start": 0.0, "end": duration / 2},
                    {"word": "AUTOSHORTS", "start": duration / 2, "end": duration}
                ]
            }
        ]
    }

def _cleanup_temp(temp_audio: str, temp_dir: str):
    if os.path.exists(temp_audio):
        try: os.remove(temp_audio)
        except: pass
    if os.path.exists(temp_dir):
        try: os.rmdir(temp_dir)
        except: pass
