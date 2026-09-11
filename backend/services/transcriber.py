import os
import subprocess
import tempfile
import json
import re
from dotenv import load_dotenv

load_dotenv()

import time

def transcribe_with_gemini(audio_path: str, lang: str = "auto", time_offset: float = 0.0) -> dict:
    """
    Transkribiert Audio über die Google Gemini API mit google.genai Client.
    Verwendet Inline Audio Bytes und eine hochgradig robuste Multi-Model Kaskade
    mit automatischem Retry bei 503/429/Overloaded.
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
        Transkribiere das gesprochene Audio Wort für Wort mit präzisen Zeitstempeln (in Sekunden als Float, relativ zum Audioanfang ab 0.0).
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
        
        # Robust multi-model cascade with retry
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-1.5-pro"
        ]
        
        response = None
        for model_name in models_to_try:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[part, prompt]
                    )
                    if response and response.text:
                        break
                except Exception as e:
                    err_str = str(e).lower()
                    if "503" in err_str or "429" in err_str or "overloaded" in err_str or "quota" in err_str:
                        print(f"Gemini {model_name} temporär ausgelastet (Versuch {attempt+1}), warte 1s...")
                        time.sleep(1.0)
                        continue
                    else:
                        print(f"Gemini Model {model_name} Hinweis: {e}")
                        break
            if response and response.text:
                break
                
        if not response or not response.text:
            return None
            
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "", 1).rsplit("```", 1)[0].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "", 1).rsplit("```", 1)[0].strip()
            
        data = json.loads(raw_text)
        if isinstance(data, dict) and "segments" in data:
            # Stelle sicher, dass jedes Segment auch 'words' mit Start/Endzeit hat und time_offset addiert wird
            for seg in data["segments"]:
                s_start = round(float(seg.get("start", 0.0)) + time_offset, 2)
                s_end = round(float(seg.get("end", s_start + 2.0)) + time_offset, 2)
                seg["start"] = s_start
                seg["end"] = s_end
                
                if "words" not in seg or not seg["words"]:
                    words_list = seg.get("text", "").strip().split()
                    if words_list:
                        dur_per_word = max(0.1, (s_end - s_start) / max(len(words_list), 1))
                        seg["words"] = [
                            {
                                "word": w,
                                "start": round(s_start + (i * dur_per_word), 2),
                                "end": round(s_start + ((i + 1) * dur_per_word), 2)
                            }
                            for i, w in enumerate(words_list)
                        ]
                else:
                    for w in seg["words"]:
                        w["start"] = round(float(w.get("start", 0.0)) + time_offset, 2)
                        w["end"] = round(float(w.get("end", w["start"] + 0.3)) + time_offset, 2)
            return data
    except Exception as e:
        print(f"Gemini Audio-Transkription Hinweis/Fehler: {e}")
    return None

def transcribe_with_local_whisper(audio_path: str, lang: str = "auto", time_offset: float = 0.0) -> dict:
    """
    100% robuster lokaler Whisper-Fallback ohne API-Kosten oder Internet-Abhängigkeit.
    Nutzt tiny/base mit Speicherschutz.
    """
    try:
        import whisper
        print(f"Starte lokales Whisper für: {os.path.basename(audio_path)}...")
        # Try tiny first for minimal memory footprint (75MB RAM)
        model = None
        for m_size in ["tiny", "base"]:
            try:
                model = whisper.load_model(m_size)
                break
            except Exception as le:
                print(f"Whisper Model {m_size} konnte nicht geladen werden: {le}")
                
        if model is None:
            return None
        
        options = {"word_timestamps": True}
        if lang and lang != "auto":
            options["language"] = lang
            
        result = model.transcribe(audio_path, **options)
        
        full_text = result.get("text", "").strip()
        raw_segments = result.get("segments", [])
        
        segments = []
        for seg in raw_segments:
            seg_start = round(float(seg.get("start", 0.0)) + time_offset, 2)
            seg_end = round(float(seg.get("end", 0.0)) + time_offset, 2)
            seg_text = seg.get("text", "").strip()
            
            words = []
            if "words" in seg and seg["words"]:
                for w in seg["words"]:
                    w_text = w.get("word", "").strip()
                    if w_text:
                        words.append({
                            "word": w_text,
                            "start": round(float(w.get("start", seg_start)) + time_offset, 2),
                            "end": round(float(w.get("end", seg_end)) + time_offset, 2)
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

def transcribe_audio(video_path: str, video_lang: str = "auto", subtitle_lang: str = "auto", start_time: float = None, duration: float = None) -> dict:
    """
    Transkribiert Audio mit Multi-Engine Kaskade:
    1. Google Gemini Audio API (blitzschnell, präzise)
    2. Lokales OpenAI Whisper (100% ausfallsicheres lokales Backup)
    3. OpenAI Whisper Cloud API (falls Key vorhanden)
    4. Robuster Dauer-Fallback
    
    Falls start_time und duration angegeben sind, wird nur der gewählte Ausschnitt
    extrahiert und die Zeitstempel exakt auf die Video-Timeline abgestimmt.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Datei nicht gefunden: {video_path}")
        
    time_offset = float(start_time) if start_time is not None and float(start_time) > 0 else 0.0
    
    # 1. Extrahiere leichtes MP3-Audio per FFmpeg (begrenzt auf maximal den gewählten Bereich)
    temp_dir = tempfile.mkdtemp()
    temp_audio = os.path.join(temp_dir, "temp_audio.mp3")
    target_file = video_path
    
    try:
        cmd = ["ffmpeg", "-y"]
        if time_offset > 0:
            cmd.extend(["-ss", str(time_offset)])
        if duration is not None and float(duration) > 0:
            cmd.extend(["-t", str(float(duration))])
        cmd.extend([
            "-i", video_path,
            "-vn", "-acodec", "libmp3lame", "-ar", "16000", "-ac", "1", "-b:a", "64k",
            temp_audio
        ])
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        target_file = temp_audio
    except Exception as e:
        print(f"FFmpeg Audio-Extraktion Hinweis ({e}), nutze Originaldatei.")
        target_file = video_path

    # Engine 1: Google Gemini Audio Transkription (Primär)
    gemini_result = transcribe_with_gemini(target_file, video_lang, time_offset)
    if gemini_result and gemini_result.get("segments") and len(gemini_result["segments"]) > 0:
        print(f"Google Gemini Transkription erfolgreich: {len(gemini_result['segments'])} Segmente.")
        _cleanup_temp(temp_audio, temp_dir)
        return gemini_result

    # Engine 2: Lokales Whisper (Ausfallsicheres Offline-Backup)
    whisper_result = transcribe_with_local_whisper(target_file, video_lang, time_offset)
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
                    start = round(float(seg.get("start", 0.0)) + time_offset, 2)
                    end = round(float(seg.get("end", 0.0)) + time_offset, 2)
                    text = str(seg.get("text", "")).strip()
                else:
                    start = round(float(getattr(seg, "start", 0.0)) + time_offset, 2)
                    end = round(float(getattr(seg, "end", 0.0)) + time_offset, 2)
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
        dur_val = float(probe.stdout.strip())
    except:
        dur_val = 30.0

    dur_val = min(dur_val, float(duration) if duration else 30.0)
    _cleanup_temp(temp_audio, temp_dir)
    return {
        "text": "MIMAROS AUTOSHORTS",
        "segments": [
            {
                "start": time_offset,
                "end": time_offset + dur_val,
                "text": "MIMAROS AUTOSHORTS",
                "words": [
                    {"word": "MIMAROS", "start": time_offset, "end": time_offset + (dur_val / 2)},
                    {"word": "AUTOSHORTS", "start": time_offset + (dur_val / 2), "end": time_offset + dur_val}
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
