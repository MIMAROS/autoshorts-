import os
import json
import asyncio
import subprocess
from dotenv import load_dotenv
from google import genai
import edge_tts
from services.html_render_engine import render_html_slide

# Load environment variables
load_dotenv()

# Setup Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)

def check_setup():
    if not api_key:
        raise ValueError("GEMINI_API_KEY ist nicht in der .env gesetzt.")
    if not client:
        raise ValueError("Google GenAI Client konnte nicht initialisiert werden.")

async def generate_script_and_prompts(topic: str) -> list:
    """
    Nutzt Gemini, um ein vollstrukturiertes Social-Media-Skript (in Szenen unterteilt)
    inklusive Imagen-Bildprompts zu generieren.
    """
    check_setup()
    
    prompt = f"""
    Du bist ein weltklasse Social-Media-Kreativer und Experte für virale Videos auf TikTok, Shorts und Reels.
    Erstelle ein extrem fesselndes Skript für ein 9:16 Kurzvideo zum Thema: "{topic}".
    Das Video soll die Mimaros-Designphilosophie widerspiegeln (minimalistisch, Premium, kognitiv optimiert, modern).
    
    Teile das Skript in 4 logische Szenen ein (Gesamtdauer ca. 30-45 Sekunden).
    Jede Szene braucht einen gesprochenen Text (speech_text) und einen hochpräzisen, detaillierten Bildgenerierungs-Prompt (visual_prompt).
    
    Die Bildprompts für Imagen 3 MÜSSEN im Mimaros-CI-Stil formuliert sein (z.B. abstract 3D render, glassmorphism, clean layouts, dark corporate tech theme). Nutze Farb-Keywords wie "dark blue #0B111A", "golden accent #C89B31" und "cyan blue #14AEEA".
    
    Liefere die Antwort exakt und AUSSCHLIESSLICH als ein gültiges JSON-Array mit 4 Objekten mit folgendem Format:
    [
        {{
            "scene_num": 1,
            "speech_text": "Gesprochener Text für diese Szene. Muss flüssig und packend klingen.",
            "visual_prompt": "Detaillierter Prompt für Imagen 3 im Mimaros-Stil."
        }},
        ...
    ]
    Gib absolut keinen Markdown-Formatierungstext, keine Erklärungen und kein "```json" drumherum zurück. Nur das rohe JSON Array!
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
    except Exception as e:
        print(f"Fehler mit gemini-2.5-flash: {e}. Versuche Fallback auf gemini-2.0-flash...")
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
            )
        except Exception as e2:
            print(f"Fehler mit gemini-2.0-flash: {e2}. Versuche Fallback auf gemini-3.1-flash-lite...")
            response = client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=prompt,
            )
    
    text = response.text.strip()
    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()
        
    try:
        scenes = json.loads(text)
        return scenes
    except Exception as e:
        print("Fehler beim Parsen des generierten Skripts:", response.text)
        raise e

async def generate_voice_audio(text: str, output_path: str):
    """
    Generiert deutsches Voice-Audio für ein Skript-Segment mit edge-tts (Microsoft Conrad Stimme).
    Edge-TTS ist kostenlos, benötigt keinen Key und klingt extrem natürlich auf Deutsch.
    """
    communicate = edge_tts.Communicate(text, "de-DE-ConradNeural")
    await communicate.save(output_path)
    return output_path

def generate_imagen_image(prompt: str, output_path: str):
    """
    Nutzt das neue Google GenAI SDK, um ein 9:16 Bild mit Imagen zu generieren.
    Triggert einen stilvollen Mimaros-CI-Fallback, falls der API-Key keine Bildrechte hat.
    """
    check_setup()
    
    # Ergänze das Mimaros CI-Styling
    full_prompt = f"{prompt}. High-end 3D visual, extreme minimalism, dark blue background #0B111A, glowing cyan #14AEEA and gold #C89B31 accents, sleek lighting, clean presentation layout, 9:16 vertical frame, shot on 35mm."
    
    print(f"Generiere Bild für Prompt: {full_prompt}")
    
    try:
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=full_prompt,
            config=dict(
                number_of_images=1,
                aspect_ratio="9:16",
                output_mime_type="image/png"
            )
        )
        
        for generated_image in response.generated_images:
            # Speichert das Bild ab
            generated_image.image.save(output_path)
            return output_path
        
        raise RuntimeError("Imagen 3 hat kein Bild zurückgeliefert.")
    except Exception as e:
        print(f"Fehler bei Imagen-Bildgenerierung: {e}")
        print("Triggere Mimaros-CI-Bildfallback (Generiere ein statisches, stilvolles Mimaros-CI-Bild)...")
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Premium 1080x1920 (9:16) Canvas
            img = Image.new('RGB', (1080, 1920), color='#0B111A')
            draw = ImageDraw.Draw(img)
            
            # Äußerer Mimaros Gold-Rahmen
            draw.rectangle([30, 30, 1050, 1890], outline='#C89B31', width=4)
            # Innerer dunkler Kontrastrahmen
            draw.rectangle([45, 45, 1035, 1875], outline='#101A24', width=2)
            
            # Bento-Grid Box im Zentrum simulieren
            draw.rectangle([100, 500, 980, 1300], fill='#101A24', outline='#14AEEA', width=3)
            
            font_title = None
            font_text = None
            try:
                # Versuche Standard-Schriftarten in Windows zu laden
                font_title = ImageFont.truetype("arial.ttf", 65)
                font_text = ImageFont.truetype("arial.ttf", 45)
            except:
                pass
            
            # Titel "MIMAROS AUTO-POST" oder ähnlich
            draw.text((540, 400), "MIMAROS EDUCATION", fill='#C89B31', font=font_title, anchor="mm")
            
            # Textzeilen für den Screen-Text
            words = prompt.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                if len(" ".join(current_line)) > 22:
                    lines.append(" ".join(current_line[:-1]))
                    current_line = [word]
            lines.append(" ".join(current_line))
            
            start_y = 700
            for line in lines:
                draw.text((540, start_y), line, fill='#FFFFFF', font=font_text, anchor="mm")
                start_y += 70
                
            # Fußzeile mit Webseite
            draw.text((540, 1750), "www.mimaros.eu", fill='#14AEEA', font=font_text, anchor="mm")
            
            img.save(output_path)
            print(f"Fallback-Bild erfolgreich unter {output_path} erstellt.")
            return output_path
        except Exception as fallback_err:
            print(f"Kritischer Fehler bei der Fallback-Bildgenerierung: {fallback_err}")
            raise e

def create_scene_clip(image_path: str, audio_path: str, output_path: str):
    """
    Verbindet das generierte Bild im Loop mit der Audiodatei der Szene zu einem MP4-Clip.
    """
    command = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path
    ]
    
    print(f"Erstelle Szenen-Clip: {output_path}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Fehler beim Erstellen des Szenen-Clips: {result.stderr}")
    return output_path

async def run_end_to_end_pipeline(topic: str, output_video_path: str, config: dict = None) -> str:
    """
    Führt die gesamte Kette vollautomatisch aus:
    1. Skript generieren
    2. Bilder & Audio pro Szene erstellen
    3. Szenen-Clips rendern
    4. Clips mit Crossfade stitchen
    5. Branding & Untertitel auf das Gesamtvideo legen
    """
    if config is None:
        config = {
            "use_master_ci": True,
            "primaryColor": "#14AEEA",
            "textColor": "#EEF3F8",
            "design": "hormozi",
            "watermark_text": "mimaros.eu"
        }
        
    temp_dir = os.path.join(os.path.dirname(output_video_path), "temp_automation")
    os.makedirs(temp_dir, exist_ok=True)
    
    print("--- SCHRITT 1: Generiere Skript und Bild-Prompts mit Gemini ---")
    scenes = await generate_script_and_prompts(topic)
    
    clip_paths = []
    combined_transcript_segments = []
    current_time_offset = 0.0
    
    for scene in scenes:
        num = scene.get("scene_num", 1)
        speech = scene.get("speech_text", scene.get("speech", ""))
        prompt = scene.get("visual_prompt", scene.get("image_prompt", scene.get("prompt", "")))
        
        print(f"\n--- SCHRITT 2.{num}: Generiere Assets für Szene {num} ---")
        img_path = os.path.join(temp_dir, f"scene_{num}_img.png")
        aud_path = os.path.join(temp_dir, f"scene_{num}_aud.mp3")
        clip_path = os.path.join(temp_dir, f"scene_{num}_raw.mp4")
        norm_clip_path = os.path.join(temp_dir, f"scene_{num}_norm.mp4")
        
        # Audio & Bild generieren
        await generate_voice_audio(speech, aud_path)
        generate_imagen_image(prompt, img_path)
        
        # Render HTML/CSS Slide mit Mimaros Bento-Layout auf den Hintergrund
        slide_img_path = os.path.join(temp_dir, f"scene_{num}_slide.png")
        await render_html_slide(topic, speech, img_path, slide_img_path)
        
        # Rohen Szenenclip aus dem HTML-Slide-Bild und Audio rendern
        create_scene_clip(slide_img_path, aud_path, clip_path)
        
        # Importiere normalisierungs-funktion aus video_processor
        from services.video_processor import normalize_clip, get_video_duration
        normalize_clip(clip_path, norm_clip_path, resolution="1080p")
        
        clip_duration = get_video_duration(norm_clip_path)
        
        # Erstelle ein Mock-Transcript-Segment für die Untertitel
        combined_transcript_segments.append({
            "start": current_time_offset,
            "end": current_time_offset + clip_duration,
            "text": speech
        })
        current_time_offset += clip_duration
        
        clip_paths.append(norm_clip_path)
        
    print("\n--- SCHRITT 3: Clips zusammenschneiden (Crossfade) ---")
    from services.video_processor import stitch_clips, apply_branding_and_subs
    
    stitched_path = os.path.join(temp_dir, "stitched_final.mp4")
    stitch_clips(clip_paths, stitched_path)
    
    print("\n--- SCHRITT 4: Branding, Untertitel und Logo hinzufügen ---")
    transcript_data = {
        "segments": combined_transcript_segments
    }
    
    apply_branding_and_subs(stitched_path, transcript_data, output_video_path, config)
    
    print(f"\n[ERFOLG] VOLLAUTOMATISCHES VIDEO ERFOLGREICH ERSTELLT: {output_video_path}")
    
    # Cleanup temp files
    try:
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
        os.rmdir(temp_dir)
    except Exception as e:
        print("Fehler beim Temp-Cleanup:", e)
        
    return output_video_path
