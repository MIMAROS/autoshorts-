import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# API Key Konfiguration
api_key = os.getenv("GEMINI_API_KEY")

def _get_genai_client():
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Fehler beim Erstellen des GenAI Clients: {e}")
        return None

def analyze_hooks(transcript_segments: list, clip_length: str = "auto") -> list:
    """
    Sendet das Transkript an Gemini und erhält die besten Passagen basierend auf clip_length.
    Erwartet wird ein JSON Array von Hooks inkl. viral_score.
    """
    client = _get_genai_client()
    if not client:
        print("GEMINI_API_KEY nicht gesetzt oder Client nicht verfügbar, nutze Standard-Hook...")
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
        Du bist ein Experte für virale Social-Media-Videos (TikTok, YouTube Shorts, Instagram Reels).
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
        ]
        Hier ist das Transkript mit Zeitstempeln (nutze diese für start_time_approx und end_time_approx):
        {transcript_with_times}
        """
        
        response = None
        for m_name in ["gemini-2.5-flash", "gemini-flash-latest", "gemini-3.7-flash", "gemini-3.6-flash"]:
            try:
                response = client.models.generate_content(model=m_name, contents=prompt)
                if response and response.text:
                    break
            except Exception:
                continue
                
        if response and response.text:
            text = response.text.strip()
            if text.startswith("```json"):
                text = text.replace("```json", "", 1).rsplit("```", 1)[0].strip()
            elif text.startswith("```"):
                text = text.replace("```", "", 1).rsplit("```", 1)[0].strip()
                
            raw_data = json.loads(text)
            results = []
            for idx, clip in enumerate(raw_data):
                hook = {
                    "id": idx + 1,
                    "start_time_approx": float(clip.get("start_time_approx", 0.0)),
                    "end_time_approx": float(clip.get("end_time_approx", 30.0)),
                    "rationale": clip.get("rationale", "Spannender Ausschnitt"),
                    "viral_score": int(clip.get("viral_score", 90)),
                    "title": str(clip.get("title", f"CLIP {idx+1}")).upper(),
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
        
    client = _get_genai_client()
    if not client:
        words = [w for w in transcript_text.strip().split() if len(w) > 2][:4]
        return " ".join(words).upper() if words else "VIDEO HOOK"
        
    try:
        prompt = f"""
        Du bist ein Social-Media-Experte für Kurzvideos (TikTok, YouTube Shorts, Instagram Reels).
        Hier ist das gesprochene Transkript eines Videos:
        "{transcript_text[:1200]}"
        
        Generiere basierend auf EXAKT diesem inhaltlichen Kontext einen extrem kurzen, prägnanten Hook-Titel (max. 3 bis 5 Worte in GROSSBUCHSTABEN).
        Der Titel MUSS sich zwingend auf das tatsächliche Thema beziehen (z.B. "DER GRÖSSTE VERTRIEBSFEHLER", "AUTOMATISIERE DEIN MARKETING", "3 TIPPS FÜR MEHR UMSATZ").
        Keinerlei generische Clickbait-Floskeln ohne Themenbezug.
        Antworte AUSSCHLIESSLICH mit dem reinen Titel in GROSSBUCHSTABEN (keine Anführungszeichen, kein Markdown, keine Erklärung).
        """
        
        response = None
        for m_name in ["gemini-2.5-flash", "gemini-flash-latest", "gemini-3.7-flash", "gemini-3.6-flash"]:
            try:
                response = client.models.generate_content(model=m_name, contents=prompt)
                if response and response.text:
                    break
            except Exception:
                continue
                
        if response and response.text:
            title = response.text.strip().replace('"', '').replace("'", "").replace("*", "").strip()
            # Falls mehrzeilig, nimm die erste nicht-leere Zeile
            lines = [l.strip() for l in title.splitlines() if l.strip()]
            if lines:
                title = lines[0]
            if title:
                return title.upper()
                
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
        return "🔥 Schau dir dieses virale Short an!\n\n#viral #shorts #mimaros"
        
    client = _get_genai_client()
    if not client:
        return f"🔥 {transcript_text[:100]}...\n\n#viral #shorts #mimaros"
        
    try:
        prompt = f"""
        Du bist ein Social-Media-Manager für TikTok, Instagram Reels und YouTube Shorts im B2B / High-Performance Bereich.
        Hier ist das gesprochene Transkript eines Videos:
        "{transcript_text[:1200]}"
        
        Schreibe eine ansprechende, hoch-konvertierende Social-Media-Beschreibung für diesen Beitrag auf Deutsch.
        Sie sollte enthalten:
        1. Einen knackigen Hook im ersten Satz mit passendem Emoji.
        2. 2-3 Sätze Zusammenfassung / Kernaussage mit echtem Mehrwert.
        3. Eine aktivierende Frage / Call-to-Action für die Kommentare.
        4. 3-5 relevante Hashtags (z.B. #b2b #marketing #mimaros #shorts).
        
        Antworte direkt mit dem fertigen Text.
        """
        
        response = None
        for m_name in ["gemini-2.5-flash", "gemini-flash-latest", "gemini-3.7-flash", "gemini-3.6-flash"]:
            try:
                response = client.models.generate_content(model=m_name, contents=prompt)
                if response and response.text:
                    break
            except Exception:
                continue
                
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print(f"Fehler bei Social Caption Generierung: {e}")
        
    return f"🔥 {transcript_text[:150]}...\n\n#viral #shorts #mimaros"
