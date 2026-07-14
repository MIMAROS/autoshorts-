import whisper
import os
import threading

# Laden des Modells (wir nutzen das kleine "base" oder "small" Modell, um Ressourcen zu sparen)
# Beim ersten Start wird das Modell von OpenAI heruntergeladen.
# Für produktiven, kostenlosen Einsatz ist "base" ein guter Kompromiss aus Geschwindigkeit und Genauigkeit.
MODEL_NAME = "tiny"
print(f"Lade lokales Whisper Modell '{MODEL_NAME}' (dies kann beim ersten Mal kurz dauern)...")
model = whisper.load_model(MODEL_NAME)

# Whisper is not thread-safe, so we need a lock for concurrent FastAPI background tasks
transcribe_lock = threading.Lock()

def transcribe_audio(video_path: str, video_lang: str = "auto", subtitle_lang: str = "auto") -> dict:
    """
    Transkribiert das Audio aus dem Video mit genauen Zeitstempeln (Wort-Ebene).
    Wir nutzen word_timestamps=True für den Schnitt der Hooks.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video nicht gefunden: {video_path}")
        
    print(f"Starte Transkription für: {video_path}")
    
    # Whisper arguments
    transcribe_args = {"word_timestamps": True}
    if video_lang != "auto":
        transcribe_args["language"] = video_lang
    if subtitle_lang == "en" and video_lang != "en":
        transcribe_args["task"] = "translate"
    
    # Transkription mit Wort-Zeitstempeln innerhalb eines Locks
    with transcribe_lock:
        result = model.transcribe(video_path, **transcribe_args)
    
    # Extrahiere das Transkript und die Segmente
    return {
        "text": result["text"],
        "segments": result["segments"]
    }
