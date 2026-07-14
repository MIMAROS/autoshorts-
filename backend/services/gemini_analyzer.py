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
        raise ValueError("GEMINI_API_KEY ist nicht in der .env gesetzt. Bitte kostenlosen Key eintragen.")
        
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    transcript_with_times = ""
    for seg in transcript_segments:
        start_m = int(seg['start'] // 60)
        start_s = int(seg['start'] % 60)
        transcript_with_times += f"[{start_m:02d}:{start_s:02d}] {seg['text']}\n"

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
            "title": "Titel des Clips",
            "social_media_caption": "Virale Beschreibung mit starkem Hook, einer Frage/Call-to-Action und passenden Hashtags."
        }}
    ] Achte darauf, dass 'viral_score' eine Zahl zwischen 0 und 100 ist, die das virale Potenzial einschätzt.
    Hier ist das Transkript mit Zeitstempeln (nutze diese für start_time_approx und end_time_approx):
    {transcript_with_times}
    """
    
    response = model.generate_content(prompt)
    
    # Extrahiere JSON (falls Gemini Markdown-Codeblöcke nutzt)
    text = response.text
    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()
        
    try:
        raw_data = json.loads(text)
        results = []
        for idx, clip in enumerate(raw_data):
            hook = {
                "id": idx + 1,
                "start_time_approx": clip.get("start_time_approx"),
                "end_time_approx": clip.get("end_time_approx"),
                "rationale": clip.get("rationale"),
                "viral_score": clip.get("viral_score"),
                "title": clip.get("title", f"Clip {idx+1}"),
                "social_media_caption": clip.get("social_media_caption", "Schau dir dieses virale Video an! 🔥 #viral #shorts")
            }
            results.append(hook)
        return results
            
    except Exception as e:
        print("Fehler beim Parsen der Gemini-Antwort:", response.text)
        raise e
