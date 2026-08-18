import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Der Nutzer muss seinen API-Key in die .env Datei eintragen: GEMINI_API_KEY=xxx
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def analyze_hooks(transcript_segments: list, clip_length: str = "auto") -> list:
    """
    Sendet das Transkript an Gemini und erhält die besten Passagen basierend auf clip_length.
    Erwartet wird ein JSON Array von Hooks inkl. viral_score.
    """
    if not api_key:
        print("GEMINI_API_KEY nicht gesetzt, nutze Standard-Hook...")
        return [{
            "id": 1,
            "start_time_approx": 0.0,
            "end_time_approx": 30.0,
            "rationale": "Standard Hook",
            "viral_score": 90,
            "title": "VIRAL SHORT",
            "social_media_caption": "Schau dir dieses virale Video an! 🔥 #viral #shorts"
        }]
        
    try:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
        except:
            model = genai.GenerativeModel('gemini-1.5-flash')
        
        transcript_with_times = ""
        for seg in transcript_segments:
            start_m = int(seg.get('start', 0) // 60)
            start_s = int(seg.get('start', 0) % 60)
            transcript_with_times += f"[{start_m:02d}:{start_s:02d}] {seg.get('text', '')}\n"

        length_instruction = "30-60 Sekunden"
        if clip_length == "short":
            length_instruction = "unter 30 Sekunden"
        elif clip_length == "extended":
            length_instruction = "60-90 Sekunden"

        prompt = f"""
        Du bist ein Experte für virale Social-Media-Videos (TikTok, YouTube Shorts).
        Analysiere das folgende Transkript und finde die 3 spannendsten Passagen (Hooks), die sich perfekt für {length_instruction} lange 9:16 Shorts eignen.
        
        Liefere die Antwort exakt und AUSSCHLIESSLICH als gültiges JSON-Array mit 3 Objekten. Die Antwort MUSS ZWINGEND ein valides JSON Array sein mit folgendem Format:
        [
            {{
                "start_time_approx": float,
                "end_time_approx": float,
                "rationale": "Kurze Erklärung",
                "viral_score": int (0-100),
                "title": "Ein stark klickbarer, viraler Hook/Titel des Clips (max. 3-5 Wörter in GROSSBUCHSTABEN, z.B. DER GEHEIME TRICK)",
                "social_media_caption": "Virale Beschreibung mit starkem Hook, einer Frage/Call-to-Action und passenden Hashtags."
            }}
        ] Achte darauf, dass 'viral_score' eine Zahl zwischen 0 und 100 ist, die das virale Potenzial einschätzt.
        Hier ist das Transkript mit Zeitstempeln (nutze diese für start_time_approx und end_time_approx):
        {transcript_with_times}
        """
        
        response = model.generate_content(prompt)
        
        # Extrahiere JSON (falls Gemini Markdown-Codeblöcke nutzt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        elif text.startswith("```"):
            text = text.replace("```", "").strip()
            
        raw_data = json.loads(text)
        results = []
        for idx, clip in enumerate(raw_data):
            hook = {
                "id": idx + 1,
                "start_time_approx": clip.get("start_time_approx", 0.0),
                "end_time_approx": clip.get("end_time_approx", 30.0),
                "rationale": clip.get("rationale", "Spannender Ausschnitt"),
                "viral_score": clip.get("viral_score", 90),
                "title": clip.get("title", f"Clip {idx+1}"),
                "social_media_caption": clip.get("social_media_caption", "Schau dir dieses virale Video an! 🔥 #viral #shorts")
            }
            results.append(hook)
        if results:
            return results
                
    except Exception as e:
        print("Hinweis bei Gemini Hook-Analyse:", e)
        
    # Ausfallsicherer Fallback
    dur = 30.0
    if transcript_segments:
        try:
            dur = min(float(transcript_segments[-1].get("end", 30.0)), 60.0)
        except:
            dur = 30.0
    return [{
        "id": 1,
        "start_time_approx": 0.0,
        "end_time_approx": max(dur, 10.0),
        "rationale": "Automatischer Video-Ausschnitt",
        "viral_score": 95,
        "title": "VIRAL SHORT",
        "social_media_caption": "Schau dir dieses Video an! 🔥 #shorts #viral"
    }]

def generate_context_aware_title(transcript_text: str) -> str:
    """
    Generiert basierend auf dem echten gesprochenen Inhalt des Videos (Transkript)
    einen extrem kurzen, prägnanten Hook-Titel (max. 3-5 Wörter in GROSSBUCHSTABEN).
    """
    if not transcript_text or not transcript_text.strip():
        return "VIDEO HOOK"
        
    if not api_key:
        words = [w for w in transcript_text.strip().split() if len(w) > 2][:4]
        return " ".join(words).upper() if words else "VIDEO HOOK"
        
    try:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
        except:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
        prompt = f"""
        Du bist ein Social-Media-Experte für Kurzvideos (TikTok, Shorts, Reels).
        Hier ist das gesprochene Transkript eines Kurzvideos:
        "{transcript_text[:1000]}"
        
        Generiere basierend auf EXAKT diesem inhaltlichen Kontext einen extrem kurzen, prägnanten Hook-Titel (max. 3-5 Worte in GROSSBUCHSTABEN).
        Der Titel MUSS sich zwingend auf das tatsächliche Thema beziehen. Keinerlei generische Clickbait-Floskeln ("DAS DARFST DU NICHT VERPASSEN", "VIRALES DING").
        Antworte AUSSCHLIESSLICH mit dem nackten Titel-Text ohne Anführungszeichen, ohne Markdown und ohne Erklärung.
        """
        response = model.generate_content(prompt)
        title = response.text.strip().replace('"', '').replace("'", "")
        return title.upper() if title else " ".join(transcript_text.strip().split()[:4]).upper()
    except Exception as e:
        print(f"Fehler bei kontextbezogener Titel-Generierung: {e}")
        words = [w for w in transcript_text.strip().split() if len(w) > 2][:4]
        return " ".join(words).upper() if words else "VIDEO HOOK"

def generate_social_caption(transcript_text: str) -> str:
    """
    Generiert basierend auf dem echten gesprochenen Inhalt des Videos (Transkript)
    eine ansprechende Social-Media-Beschreibung inkl. Hook, Call-to-Action und Hashtags.
    """
    if not transcript_text or not transcript_text.strip():
        return "🔥 Schau dir dieses virale Short an!\n\n#viral #shorts #content"
        
    if not api_key:
        return f"🔥 {transcript_text[:100]}...\n\n#viral #shorts #content"
        
    try:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
        except:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
        prompt = f"""
        Du bist ein Social-Media-Manager für TikTok, Instagram Reels und YouTube Shorts.
        Hier ist das gesprochene Transkript eines Kurzvideos:
        "{transcript_text[:1000]}"
        
        Schreibe eine ansprechende, hoch-konvertierende Social-Media-Beschreibung für diesen Beitrag.
        Sie sollte enthalten:
        1. Einen knackigen Hook im ersten Satz.
        2. 2-3 Sätze Zusammenfassung / Mehrwert.
        3. Eine Frage / Call-to-Action für Kommentare.
        4. 3-5 relevante Hashtags.
        
        Antworte direkt mit dem fertigen Text.
        """
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "🔥 Schau dir dieses Video an!\n\n#viral #shorts"
    except Exception as e:
        print(f"Fehler bei Social Caption Generierung: {e}")
        return f"🔥 {transcript_text[:150]}...\n\n#viral #shorts"
