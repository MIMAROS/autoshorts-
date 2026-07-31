import os
import uuid
import asyncio
import edge_tts
from gtts import gTTS

def generate_voiceover_audio(text: str, voice: str = "alloy", lang: str = "de") -> str:
    """
    Generiert eine realistische KI-Sprecherstimme (.mp3) aus einem eingegebenen Text.
    Nutzt OpenAI (falls KEY vorhanden) oder Microsoft Edge Neural / gTTS als ausfallsicheren Standard.
    """
    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Fertige_Shorts")
    os.makedirs(export_dir, exist_ok=True)
    
    file_id = uuid.uuid4().hex[:10]
    output_filename = f"voiceover_{file_id}.mp3"
    output_path = os.path.join(export_dir, output_filename)
    
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    
    # 1. Versuche OpenAI tts-1 falls Key vorhanden
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice if voice in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"] else "alloy",
                input=text
            )
            response.stream_to_file(output_path)
            print(f"OpenAI TTS Audio erfolgreich generiert: {output_path}")
            return output_filename
        except Exception as e:
            print(f"OpenAI TTS Fehler, verwende Edge Neural Voice Fallback: {e}")
            
    # 2. Versuche Edge-TTS (Höchste neuronale Qualität, kostenlos)
    try:
        edge_voice = "de-DE-KillianNeural" if lang in ["de", "auto"] else "en-US-ChristopherNeural"
        if voice == "echo":
            edge_voice = "de-DE-KatjaNeural"
        elif voice == "nova":
            edge_voice = "en-US-JennyNeural"
            
        async def run_edge_tts():
            communicate = edge_tts.Communicate(text, edge_voice)
            await communicate.save(output_path)
            
        asyncio.run(run_edge_tts())
        print(f"Edge-TTS Neural Audio erfolgreich generiert: {output_path}")
        return output_filename
    except Exception as e:
        print(f"Edge-TTS Fehler, verwende gTTS Fallback: {e}")
        
    # 3. Fallback: gTTS
    try:
        tts = gTTS(text=text, lang='de' if lang in ['de', 'auto'] else 'en')
        tts.save(output_path)
        print(f"gTTS Audio erfolgreich generiert: {output_path}")
        return output_filename
    except Exception as e:
        print(f"gTTS Fehler: {e}")
        raise e
