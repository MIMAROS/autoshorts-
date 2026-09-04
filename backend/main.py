from typing import Optional, List, Dict, Any, Union
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import uuid
import os
import json

# FFmpeg liegt als ffmpeg.exe im backend ordner
os.environ["PATH"] = os.path.dirname(os.path.abspath(__file__)) + os.pathsep + os.environ.get("PATH", "")

from services.youtube_downloader import download_video, get_video_info
from services.transcriber import transcribe_audio
from services.gemini_analyzer import analyze_hooks
from services.video_processor import process_clip, normalize_clip, stitch_clips, apply_branding_and_subs
from services import youtube_uploader, instagram_uploader, tiktok_uploader, linkedin_uploader
from services.supabase_client import upload_file_to_supabase

app = FastAPI(title="MIMAROS Multi-Platform Auto Posting API")

# Ordner bereitstellen
export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Fertige_Shorts")
os.makedirs(export_dir, exist_ok=True)
app.mount("/videos", StaticFiles(directory=export_dir), name="videos")

import asyncio
from datetime import datetime

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_uploader_task())

async def background_uploader_task():
    while True:
        try:
            now = datetime.now()
            for s in schedules:
                if not s.get("uploaded"):
                    try:
                        scheduled_time = datetime.strptime(s["schedule_date"], "%Y-%m-%d %H:%M")
                        if now >= scheduled_time:
                            platforms = s.get("platforms", [])
                            print(f"Verarbeite Multi-Plattform Upload: {s.get('video_url')} für {platforms}")
                            
                            filename = s["video_url"].split("/videos/")[-1] if "/videos/" in s.get("video_url", "") else os.path.basename(s.get("video_url", ""))
                            local_path = os.path.join(export_dir, filename)
                            
                            caption = s.get("caption", "MIMAROS AutoShorts Video #shorts #viral")
                            
                            # 1. YouTube Shorts
                            if "YouTube Shorts" in platforms:
                                if youtube_uploader.is_authenticated():
                                    try:
                                        youtube_uploader.upload_short(local_path, s.get("title", caption.split("\n")[0][:60]), caption, "public")
                                        print("YouTube Shorts Upload erfolgreich!")
                                    except Exception as ye:
                                        print(f"Fehler bei YouTube Upload: {ye}")
                                else:
                                    print("YouTube nicht authentifiziert. Überspringe YouTube.")
                                    
                            # 2. Instagram Reels
                            if "Instagram Reels" in platforms or "Instagram" in platforms:
                                if instagram_uploader.is_authenticated():
                                    try:
                                        public_vid_url = s.get("video_url")
                                        if not public_vid_url.startswith("http"):
                                            public_vid_url = upload_file_to_supabase(local_path, "autoshorts-storage", filename) or f"http://127.0.0.1:8000/videos/{filename}"
                                        instagram_uploader.upload_reel(public_vid_url, caption)
                                        print("Instagram Reel Upload erfolgreich!")
                                    except Exception as ie:
                                        print(f"Fehler bei Instagram Upload: {ie}")
                                else:
                                    print("Instagram nicht authentifiziert. Überspringe Instagram.")
                                    
                            # 3. TikTok
                            if "TikTok" in platforms:
                                if tiktok_uploader.is_authenticated():
                                    try:
                                        tiktok_uploader.upload_video(local_path, caption[:150])
                                        print("TikTok Upload erfolgreich!")
                                    except Exception as te:
                                        print(f"Fehler bei TikTok Upload: {te}")
                                else:
                                    print("TikTok nicht authentifiziert. Überspringe TikTok.")

                            # 4. LinkedIn
                            if "LinkedIn" in platforms:
                                if linkedin_uploader.is_authenticated():
                                    try:
                                        linkedin_uploader.upload_video(local_path, caption, s.get("title", "MIMAROS Video"))
                                        print("LinkedIn Video Upload erfolgreich!")
                                    except Exception as le:
                                        print(f"Fehler bei LinkedIn Upload: {le}")
                                else:
                                    print("LinkedIn nicht authentifiziert. Überspringe LinkedIn.")
                                    
                            s["uploaded"] = True
                    except ValueError:
                        pass
        except Exception as e:
            print(f"Error in background uploader: {e}")
        
        await asyncio.sleep(30)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory Speicher für Jobs (in Produktion durch Datenbank ersetzen)
jobs = {}
schedules = []

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.json")

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

class VideoRequest(BaseModel):
    youtube_url: str
    resolution: str = "720p"
    subtitle_config: dict = {}
    clip_length: str = "auto"
    video_lang: str = "auto"
    subtitle_lang: str = "auto"
    trim_start: int = None
    trim_end: int = None

class VideoInfoRequest(BaseModel):
    youtube_url: str

class SearchRequest(BaseModel):
    query: str
    limit: int = 8

class TitleRequest(BaseModel):
    text: str

from typing import List

class ScheduleRequest(BaseModel):
    job_id: str
    video_url: str = ""
    platforms: List[str]
    schedule_date: str
    caption: str = ""

def parse_time(time_val) -> float:
    # Falls time_val bereits ein float oder int ist (von Gemini neues Format)
    if isinstance(time_val, (int, float)):
        return float(time_val)
    # Wandelt MM:SS in Sekunden um falls es ein string ist
    if isinstance(time_val, str):
        parts = time_val.split(":")
        if len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
    return 0.0

def process_video_task(job_id: str, url: str, resolution: str, subtitle_config: dict, clip_length: str = "auto", video_lang: str = "auto", subtitle_lang: str = "auto", is_local: bool = False, local_path: str = "", trim_start: int = None, trim_end: int = None):
    try:
        jobs[job_id] = {"status": "downloading", "progress": 10, "hooks": [], "clips": []}
        
        # 1. Video herunterladen (oder lokales Video nutzen)
        if is_local:
            if trim_start is not None and trim_end is not None and trim_end > trim_start:
                # Trimming local file with FFmpeg
                import subprocess
                trimmed_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
                os.makedirs(trimmed_dir, exist_ok=True)
                trimmed_path = os.path.join(trimmed_dir, f"{job_id}_trimmed.mp4")
                duration = trim_end - trim_start
                try:
                    subprocess.run(["ffmpeg", "-y", "-ss", str(trim_start), "-t", str(duration), "-i", local_path, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", trimmed_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    video_path = trimmed_path
                except Exception as e:
                    print(f"Fehler beim lokalen Trimming: {e}")
                    video_path = local_path
            else:
                video_path = local_path
        else:
            temp_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", job_id)
            os.makedirs(temp_output, exist_ok=True)
            video_path = download_video(url, output_path=temp_output, trim_start=trim_start, trim_end=trim_end)
        
        # 2. Transkribieren (Whisper)
        jobs[job_id] = {"status": "transcribing", "progress": 40, "hooks": [], "clips": []}
        transcript_data = transcribe_audio(video_path, video_lang, subtitle_lang)
        
        # KI Voiceover Transkription Sync Check
        voiceover_url = subtitle_config.get("voiceoverUrl")
        if voiceover_url:
            v_filename = os.path.basename(voiceover_url)
            v_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Fertige_Shorts", v_filename)
            if not os.path.exists(v_path):
                v_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Fertige_Shorts", v_filename)
            if os.path.exists(v_path):
                subtitle_config["voiceover_path"] = v_path
                try:
                    v_transcript = transcribe_audio(v_path, video_lang, subtitle_lang)
                    if v_transcript and v_transcript.get("segments"):
                        transcript_data = v_transcript
                except Exception as e:
                    print(f"Fehler bei Voiceover Transkription: {e}")
        
        # 3. BLOCKIERENDES TIMING für LLM: Aufruf ERST NACHDEM die Whisper-Transkription abgeschlossen ist!
        jobs[job_id] = {"status": "analyzing", "progress": 70, "hooks": [], "clips": []}
        
        full_transcript_text = " ".join([seg.get("text", "") for seg in transcript_data.get("segments", [])]).strip()
        custom_header = (subtitle_config.get("hookHeader") or "").strip()
        
        if custom_header:
            context_title = custom_header
            social_caption = f"{custom_header}\n\n#shorts #viral"
        else:
            try:
                from services.gemini_analyzer import generate_context_aware_title, generate_social_caption
                if full_transcript_text and len(full_transcript_text) > 3:
                    context_title = generate_context_aware_title(full_transcript_text)
                    social_caption = generate_social_caption(full_transcript_text)
                else:
                    context_title = "VIRAL SHORT"
                    social_caption = "Schau dir dieses Video an!\n\n#shorts #content"
            except Exception as e:
                print(f"Fehler bei LLM Titel/Caption Generierung aus Transkript: {e}")
                context_title = "VIRAL SHORT"
                social_caption = f"{context_title}\n\n#shorts #content"
            
        subtitle_config["hookHeader"] = context_title
        subtitle_config["showTitle"] = subtitle_config.get("showTitle", True)
        subtitle_config["showSubtitles"] = subtitle_config.get("showSubtitles", True)
        hook_title = context_title.upper()
        
        # Aktualisiere Job-Zustand mit den aus dem Transkript generierten Daten
        jobs[job_id]["generated_title"] = context_title
        jobs[job_id]["generated_caption"] = social_caption
        jobs[job_id]["transcript_text"] = full_transcript_text
        
        # HARTER 1:1 ISOLATIONS-GUARD (OPTION A - STRIKT EINZELNES VIDEO, KEINE HIGHLIGHT-ERKENNUNG)
        modus1_opt = str(subtitle_config.get("modus1Option") or subtitle_config.get("modus1_option") or subtitle_config.get("modus") or "").lower().strip()
        selected_mode = str(subtitle_config.get("selectedMode") or subtitle_config.get("mode") or "").lower().strip()
        req_clip_len = str(clip_length).lower().strip()
        
        is_one_to_one = (
            modus1_opt in ["one_to_one", "1:1", "single", "1-to-1"] or 
            (selected_mode in ["standard", "single", "1:1", "one_to_one"] and modus1_opt != "auto_highlights") or 
            req_clip_len in ["1:1", "single", "full"]
        )
        
        if is_one_to_one:
            # OPTION A: STRIKT ISOLIERTER 1:1 EXPORT (KEIN SPLITTING, KEIN GEMINI HIGHLIGHT CALL)
            jobs[job_id] = {"status": "editing", "progress": 85, "hooks": [], "clips": []}
            
            # Ermittle tatsächliche Dauer der heruntergeladenen/gespeicherten Videodatei
            import subprocess
            try:
                probe = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                    capture_output=True, text=True, check=True
                )
                total_video_dur = float(probe.stdout.strip())
            except Exception as e:
                if transcript_data.get("segments"):
                    total_video_dur = float(transcript_data["segments"][-1].get("end", 60.0))
                else:
                    total_video_dur = 60.0

            # Da video_path bei trim_start/trim_end bereits zugeschnitten ist (oder das volle Video ist),
            # ist der relative Startpunkt in video_path IMMER 0.0 und die Endzeit total_video_dur!
            start_sec = 0.0
            end_sec = total_video_dur
                        
            single_hook = {
                "title": hook_title,
                "start_time_approx": 0.0,
                "end_time_approx": end_sec,
                "rationale": "Option A - 1:1 Video (Strikt einzelnes 1:1 Video)",
                "social_media_caption": social_caption,
                "viral_score": 100
            }
            
            export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Fertige_Shorts")
            os.makedirs(export_dir, exist_ok=True)
            output_filename = f"AutoShort_{job_id}_1to1.mp4"
            output_clip = os.path.join(export_dir, output_filename)
            
            process_clip(video_path, transcript_data, start_sec, end_sec, output_clip, resolution, subtitle_config)
            
            public_url = upload_file_to_supabase(output_clip, "autoshorts-storage", output_filename)
            final_clip_url = public_url if public_url else f"/videos/{output_filename}"
            if public_url:
                try: os.remove(output_clip)
                except: pass
                
            hooks = [single_hook]
            clips = [final_clip_url]
            
            jobs[job_id] = {
                "status": "done", 
                "progress": 100, 
                "hooks": hooks, 
                "clips": clips, 
                "generated_title": context_title, 
                "generated_caption": social_caption
            }
            
            # In Historie speichern
            history = load_db()
            history.insert(0, {
                "job_id": job_id,
                "title": hook_title,
                "thumbnail": clips[0],
                "clips": clips
            })
            save_db(history)
            return

        # OPTION B: MULTI-CLIP HIGHLIGHT ERKENNUNG (NUR FÜR AUTO-HIGHLIGHTS / YOUTUBE)
        if trim_start is not None and trim_end is not None and trim_end > trim_start:
            # Da video_path bereits vorab zugeschnitten wurde, beginnt die Datei bei 0.0
            hooks = [{
                "title": hook_title,
                "start_time_approx": "00:00",
                "end_time_approx": f"{int(trim_end - trim_start)}",
                "rationale": "Vom Nutzer definierter Zeitbereich mit Smart Trimming",
                "social_media_caption": social_caption,
                "viral_score": 95
            }]
        else:
            hooks = analyze_hooks(transcript_data["segments"], clip_length)
        
        # 4. Videoschnitt & Untertitel
        jobs[job_id] = {"status": "editing", "progress": 85, "hooks": hooks, "clips": []}
        
        clips = []
        export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Fertige_Shorts")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        for i, hook in enumerate(hooks):
            start = parse_time(hook.get("start_time_approx", "00:00"))
            end = parse_time(hook.get("end_time_approx", "00:30"))
            
            output_filename = f"AutoShort_{job_id}_Hook_{i+1}.mp4"
            output_clip = os.path.join(export_dir, output_filename)
            processed_clip = process_clip(video_path, transcript_data, start, end, output_clip, resolution, subtitle_config)
            
            # SUPABASE UPLOAD
            public_url = upload_file_to_supabase(output_clip, "autoshorts-storage", output_filename)
            if public_url:
                clips.append(public_url)
                try: os.remove(output_clip)
                except: pass
            else:
                clips.append(f"/videos/{output_filename}")
        
        jobs[job_id] = {"status": "done", "progress": 100, "hooks": hooks, "clips": clips, "generated_title": context_title, "generated_caption": social_caption}
        
        # In Historie abspeichern
        history = load_db()
        history.insert(0, {
            "job_id": job_id,
            "title": hooks[0]["title"] if hooks else "Video Projekt",
            "thumbnail": clips[0] if clips else None,
            "clips": clips
        })
        save_db(history)
    except Exception as e:
        jobs[job_id] = {"status": "error", "progress": 0, "error": str(e), "hooks": [], "clips": []}
    finally:
        # Cleanup temp video file
        if 'video_path' in locals() and os.path.exists(video_path):
            try:
                os.remove(video_path)
            except Exception as e:
                print(f"Failed to remove temp file: {e}")

def process_sequence_task(job_id: str, sequence_items: list, resolution: str, subtitle_config: dict, video_lang: str, subtitle_lang: str):
    temp_files = []
    try:
        jobs[job_id] = {"status": "downloading", "progress": 10, "hooks": [], "clips": []}
        export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Fertige_Shorts")
        os.makedirs(export_dir, exist_ok=True)
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", job_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        # 1. Sammle und normalisiere alle Clips
        normalized_clips = []
        for i, item in enumerate(sequence_items):
            jobs[job_id]["progress"] = 10 + int(30 * (i / len(sequence_items)))
            
            raw_path = ""
            if item["type"] == "url":
                raw_path = download_video(item["content"], output_path=os.path.join(temp_dir, f"raw_{i}"))
            elif item["type"] == "local":
                raw_path = item["content"] # Bereits gespeicherter lokaler Pfad
                
            temp_files.append(raw_path)
            
            # Normalisieren
            norm_path = os.path.join(temp_dir, f"norm_{i}.mp4")
            normalize_clip(raw_path, norm_path, resolution)
            normalized_clips.append(norm_path)
            temp_files.append(norm_path)
            
        # 2. Stitching
        jobs[job_id] = {"status": "stitching", "progress": 50, "hooks": [], "clips": []}
        stitched_path = os.path.join(temp_dir, f"stitched.mp4")
        stitch_clips(normalized_clips, stitched_path)
        temp_files.append(stitched_path)
        
        # 3. Transkription des Master-Videos
        jobs[job_id] = {"status": "transcribing", "progress": 70, "hooks": [], "clips": []}
        transcript_data = transcribe_audio(stitched_path, video_lang, subtitle_lang)
        
        # 4. CI-Branding und Untertitel anwenden
        jobs[job_id] = {"status": "rendering", "progress": 85, "hooks": [], "clips": []}
        output_filename = f"AutoShort_{job_id}_Sequence.mp4"
        output_clip = os.path.join(export_dir, output_filename)
        
        apply_branding_and_subs(stitched_path, transcript_data, output_clip, subtitle_config)
        
        # SUPABASE UPLOAD
        public_url = upload_file_to_supabase(output_clip, "autoshorts-storage", output_filename)
        if public_url:
            clips = [public_url]
            try: os.remove(output_clip)
            except: pass
        else:
            clips = [f"/videos/{output_filename}"]
        
        # Generiere eine Dummy-Caption via Gemini oder setze einen Standard-Text, da bei Sequenzen 
        # die KI nicht unbedingt Hooks analysieren muss, wenn der User den Aufbau selbst gewählt hat.
        # Wir fügen einfach einen Hook-Eintrag hinzu, damit das Frontend ihn anzeigen kann.
        hooks = [{
            "title": "Erstellte Sequenz",
            "start_time_approx": 0.0,
            "end_time_approx": 60.0,
            "rationale": "Manuell erstellte Sequenz aus mehreren Clips.",
            "social_media_caption": "Hier ist mein neues Video! 🔥 #shorts #viral",
            "viral_score": 100
        }]
        
        jobs[job_id] = {"status": "done", "progress": 100, "hooks": hooks, "clips": clips}
        
        history = load_db()
        history.insert(0, {
            "job_id": job_id,
            "title": "Master Sequenz",
            "thumbnail": clips[0],
            "clips": clips
        })
        save_db(history)
        
    except Exception as e:
        print(f"Error in process_sequence_task: {e}")
        jobs[job_id] = {"status": "error", "progress": 0, "error": str(e), "hooks": [], "clips": []}
    finally:
        for f in temp_files:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass
        try: os.rmdir(temp_dir)
        except: pass

class VoiceoverRequest(BaseModel):
    text: str
    voice: Optional[str] = "alloy"
    lang: Optional[str] = "de"

@app.post("/api/generate-voiceover")
async def generate_voiceover(req: VoiceoverRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text darf nicht leer sein.")
    try:
        from services.tts_service import generate_voiceover_audio
        filename = generate_voiceover_audio(req.text.strip(), req.voice or "alloy", req.lang or "de")
        return {
            "status": "success",
            "audio_url": f"/videos/{filename}",
            "filename": filename
        }
    except Exception as e:
        print(f"Voiceover Fehler: {e}")
        raise HTTPException(status_code=500, detail=f"Voiceover Generierung fehlgeschlagen: {str(e)}")

@app.post("/api/analyze-trimmed-section")
async def analyze_trimmed_section(
    file: Optional[UploadFile] = File(None),
    youtube_url: Optional[str] = Form(None),
    trim_start: Optional[float] = Form(0.0),
    trim_end: Optional[float] = Form(None),
    video_lang: Optional[str] = Form("auto")
):
    """
    Transkribiert den EXAKTEN ausgewählten Video-Bereich (trim_start bis trim_end)
    und generiert daraus vollautomatisch den Titel und die Social-Media-Beschreibung.
    """
    temp_dir = tempfile.mkdtemp()
    raw_video = os.path.join(temp_dir, "raw_input.mp4")
    target_video = raw_video
    
    try:
        if file:
            with open(raw_video, "wb") as f:
                f.write(await file.read())
        elif youtube_url:
            loop = asyncio.get_event_loop()
            dl_path = await loop.run_in_executor(None, download_video, youtube_url, temp_dir)
            target_video = dl_path if dl_path and os.path.exists(dl_path) else raw_video
        else:
            raise HTTPException(status_code=400, detail="Weder Datei noch YouTube URL angegeben.")
            
        # Falls getrimmt werden soll, erstelle getrimmte Version für präzise Audio-Analyse
        t_start = float(trim_start) if trim_start is not None and float(trim_start) >= 0 else 0.0
        t_end = float(trim_end) if trim_end is not None and float(trim_end) > t_start else None
        
        if t_end and t_end > t_start:
            trimmed_video = os.path.join(temp_dir, "trimmed_section.mp4")
            duration = t_end - t_start
            try:
                subprocess.run(
                    ["ffmpeg", "-y", "-ss", str(t_start), "-t", str(duration), "-i", target_video, "-c", "copy", trimmed_video],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                if os.path.exists(trimmed_video) and os.path.getsize(trimmed_video) > 100:
                    target_video = trimmed_video
            except Exception as trim_err:
                print(f"Schnelles Trimming Hinweis ({trim_err}), nutze Originaldatei.")
                
        loop = asyncio.get_event_loop()
        
        # Audio für den Zeitbereich transkribieren
        transcript_data = await loop.run_in_executor(
            None, transcribe_audio, target_video, video_lang or "auto"
        )
        
        full_text = ""
        segments = []
        if isinstance(transcript_data, dict):
            full_text = transcript_data.get("text", "").strip()
            segments = transcript_data.get("segments", [])
            
        from services.gemini_analyzer import generate_context_aware_title, generate_social_caption
        
        title = await loop.run_in_executor(None, generate_context_aware_title, full_text)
        caption = await loop.run_in_executor(None, generate_social_caption, full_text)
        
        return {
            "status": "success",
            "transcript": full_text,
            "title": title.upper(),
            "caption": caption,
            "segments": segments
        }
    except Exception as e:
        print(f"Fehler in analyze_trimmed_section: {e}")
        return {
            "status": "fallback",
            "title": "",
            "caption": "",
            "transcript": "",
            "segments": []
        }
    finally:
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

@app.post("/api/generate-viral-title")
async def generate_viral_title(request: TitleRequest):
    import re
    cleaned_input = re.sub(r'\.[a-zA-Z0-9]+$', '', request.text or '').replace('_', ' ').replace('-', ' ').strip()
    fallback_title = cleaned_input.upper() if cleaned_input else "VIRAL SHORT"
    
    try:
        from services.gemini_analyzer import generate_context_aware_title
        loop = asyncio.get_event_loop()
        title = await loop.run_in_executor(None, generate_context_aware_title, request.text)
        return {"title": title.upper() if title else fallback_title}
    except Exception as e:
        print(f"Error generating viral title: {e}")
        return {"title": fallback_title}

@app.post("/api/search-videos")
async def search_videos(request: SearchRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Search query is required")
    try:
        from services.youtube_downloader import search_youtube_videos
        results = search_youtube_videos(request.query, max_results=request.limit or 8)
        return {"status": "success", "results": results}
    except Exception as e:
        print(f"Error in search_videos endpoint: {e}")
        return {"status": "error", "results": [], "detail": str(e)}

@app.post("/api/video-info")
async def video_info(request: VideoInfoRequest):
    if not request.youtube_url:
        raise HTTPException(status_code=400, detail="YouTube URL or search query is required")
    try:
        info = get_video_info(request.youtube_url)
        return {"status": "success", "info": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-video")
async def process_video(request: VideoRequest, background_tasks: BackgroundTasks):
    if not request.youtube_url:
        raise HTTPException(status_code=400, detail="YouTube URL is required")
    
    job_id = str(uuid.uuid4())
    background_tasks.add_task(process_video_task, job_id, request.youtube_url, request.resolution, request.subtitle_config, request.clip_length, request.video_lang, request.subtitle_lang, False, "", request.trim_start, request.trim_end)
    
    return {
        "status": "success",
        "message": "Video processing started in background.",
        "job_id": job_id
    }

from fastapi import Request

@app.post("/api/process-sequence")
async def process_sequence(
    background_tasks: BackgroundTasks,
    request: Request
):
    form = await request.form()
    # sequence_data ist ein JSON string array z.B. '[{"type":"url","content":"http..."}, {"type":"file","filename":"file_0"}]'
    sequence_data_str = form.get("sequence_data", "[]")
    sequence_config = json.loads(sequence_data_str)
    subtitle_config = json.loads(form.get("subtitle_config", "{}"))
    resolution = form.get("resolution", "720p")
    video_lang = form.get("video_lang", "auto")
    subtitle_lang = form.get("subtitle_lang", "auto")
    
    job_id = str(uuid.uuid4())
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", job_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Files speichern und items aufbauen
    sequence_items = []
    for item in sequence_config:
        if item["type"] == "url":
            sequence_items.append(item)
        elif item["type"] == "file":
            uploaded_file = form.get(item["filename"])
            if uploaded_file:
                local_path = os.path.join(temp_dir, uploaded_file.filename)
                with open(local_path, "wb") as buffer:
                    buffer.write(await uploaded_file.read())
                sequence_items.append({"type": "local", "content": local_path})
                
    background_tasks.add_task(process_sequence_task, job_id, sequence_items, resolution, subtitle_config, video_lang, subtitle_lang)
    
    return {
        "status": "success",
        "message": "Sequence processing started in background.",
        "job_id": job_id
    }

@app.post("/api/upload-logo")
async def upload_logo(file: UploadFile = File(...)):
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    from PIL import Image
    import io
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Scale to max 500px to keep it lightweight
        max_size = 500
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
        # Save as PNG to preserve transparency
        file_path = os.path.join(temp_dir, f"logo_{uuid.uuid4().hex[:8]}.png")
        image.save(file_path, "PNG")
        
        return {
            "status": "success",
            "logo_path": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logo-Verarbeitung fehlgeschlagen: {str(e)}")

@app.post("/api/upload-video")
async def upload_video(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    resolution: str = Form("720p"), 
    clip_length: str = Form("auto"),
    video_lang: str = Form("auto"),
    subtitle_lang: str = Form("auto"),
    subtitle_config: str = Form("{}"),
    trim_start: str = Form(""),
    trim_end: str = Form("")
):
    job_id = str(uuid.uuid4())
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(temp_dir, f"{job_id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    sub_config = json.loads(subtitle_config)
    
    # Parse trim_start and trim_end safely
    t_start = int(trim_start) if trim_start and trim_start.isdigit() else None
    t_end = int(trim_end) if trim_end and trim_end.isdigit() else None

    background_tasks.add_task(process_video_task, job_id, "", resolution, sub_config, clip_length, video_lang, subtitle_lang, True, file_path, t_start, t_end)
    
    return {
        "status": "success",
        "message": "Upload successful. Video processing started.",
        "job_id": job_id
    }

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/api/schedule")
async def create_schedule(request: ScheduleRequest):
    schedules.append({
        "job_id": request.job_id,
        "video_url": request.video_url,
        "platforms": request.platforms,
        "schedule_date": request.schedule_date,
        "caption": request.caption
    })
    return {"status": "success", "message": "Upload geplant."}

@app.get("/api/schedules")
async def get_schedules():
    return {"schedules": schedules}

@app.get("/api/history")
async def get_history():
    return {"history": load_db()}

class PreviewRequest(BaseModel):
    clip_path: str
    config: dict

@app.post("/api/preview-clip")
async def preview_clip(request: PreviewRequest):
    # Generiert ein 3s Preview-Video mit dem gewählten Design & CTA
    from services.video_processor import generate_preview
    
    if request.clip_path == "demo":
        abs_path = "demo"
    else:
        abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Fertige_Shorts", os.path.basename(request.clip_path))
        
    preview_filename = f"preview_{uuid.uuid4().hex[:8]}.mp4"
    preview_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Fertige_Shorts", preview_filename)
    
    try:
        generate_preview(abs_path, preview_output, request.config)
        return {"preview_url": f"/videos/{preview_filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


from fastapi.responses import RedirectResponse
from fastapi import Request

class ManualTokenRequest(BaseModel):
    token: str
    user_id: Optional[str] = ""

@app.get("/api/auth/status")
async def auth_status():
    """
    Liefert den Verbindungsstatus für YouTube, Instagram, TikTok und LinkedIn zurück.
    """
    return {
        "youtube": youtube_uploader.is_authenticated(),
        "instagram": instagram_uploader.is_authenticated(),
        "tiktok": tiktok_uploader.is_authenticated(),
        "linkedin": linkedin_uploader.is_authenticated()
    }

@app.post("/api/auth/{platform}")
async def auth_platform(platform: str, request: Request):
    """
    Initiiert den OAuth-Flow für die jeweilige Plattform.
    """
    base_url = str(request.base_url).rstrip('/')
    
    if platform == "youtube":
        redirect_uri = f"{base_url}/api/auth/youtube/callback"
        auth_url, err = youtube_uploader.get_auth_url(redirect_uri)
        if not auth_url:
            raise HTTPException(status_code=400, detail="client_secret.json fehlt oder ist unvollständig.")
        return {"auth_url": auth_url}
        
    elif platform == "instagram":
        redirect_uri = f"{base_url}/api/auth/instagram/callback"
        auth_url, err = instagram_uploader.get_auth_url(redirect_uri)
        if not auth_url:
            raise HTTPException(status_code=400, detail="INSTAGRAM_APP_ID fehlt in der .env")
        return {"auth_url": auth_url}
        
    elif platform == "tiktok":
        redirect_uri = f"{base_url}/api/auth/tiktok/callback"
        auth_url, err = tiktok_uploader.get_auth_url(redirect_uri)
        if not auth_url:
            raise HTTPException(status_code=400, detail="TIKTOK_CLIENT_KEY fehlt in der .env")
        return {"auth_url": auth_url}

    elif platform == "linkedin":
        redirect_uri = f"{base_url}/api/auth/linkedin/callback"
        auth_url, err = linkedin_uploader.get_auth_url(redirect_uri)
        if not auth_url:
            raise HTTPException(status_code=400, detail="LINKEDIN_CLIENT_ID fehlt in der .env")
        return {"auth_url": auth_url}
        
    raise HTTPException(status_code=400, detail=f"Ungültige Plattform: {platform}")

@app.get("/api/auth/youtube/callback")
async def youtube_auth_callback(code: str, request: Request):
    base_url = str(request.base_url).rstrip('/')
    redirect_uri = f"{base_url}/api/auth/youtube/callback"
    try:
        youtube_uploader.fetch_token_from_code(code, redirect_uri)
        return RedirectResponse(url="/?connected=youtube")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube Authentifizierung fehlgeschlagen: {str(e)}")

@app.get("/api/auth/instagram/callback")
async def instagram_auth_callback(code: str, request: Request):
    base_url = str(request.base_url).rstrip('/')
    redirect_uri = f"{base_url}/api/auth/instagram/callback"
    try:
        instagram_uploader.fetch_token_from_code(code, redirect_uri)
        return RedirectResponse(url="/?connected=instagram")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Instagram Authentifizierung fehlgeschlagen: {str(e)}")

@app.get("/api/auth/tiktok/callback")
async def tiktok_auth_callback(code: str, request: Request):
    base_url = str(request.base_url).rstrip('/')
    redirect_uri = f"{base_url}/api/auth/tiktok/callback"
    try:
        tiktok_uploader.fetch_token_from_code(code, redirect_uri)
        return RedirectResponse(url="/?connected=tiktok")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TikTok Authentifizierung fehlgeschlagen: {str(e)}")

@app.get("/api/auth/linkedin/callback")
async def linkedin_auth_callback(code: str, request: Request):
    base_url = str(request.base_url).rstrip('/')
    redirect_uri = f"{base_url}/api/auth/linkedin/callback"
    try:
        linkedin_uploader.fetch_token_from_code(code, redirect_uri)
        return RedirectResponse(url="/?connected=linkedin")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LinkedIn Authentifizierung fehlgeschlagen: {str(e)}")

@app.post("/api/auth/{platform}/disconnect")
async def disconnect_platform(platform: str):
    if platform == "youtube":
        token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "youtube_token.json")
        if os.path.exists(token_file):
            try: os.remove(token_file)
            except: pass
        return {"status": "success", "message": "YouTube getrennt."}
    elif platform == "instagram":
        instagram_uploader.disconnect()
        return {"status": "success", "message": "Instagram getrennt."}
    elif platform == "tiktok":
        tiktok_uploader.disconnect()
        return {"status": "success", "message": "TikTok getrennt."}
    elif platform == "linkedin":
        linkedin_uploader.disconnect()
        return {"status": "success", "message": "LinkedIn getrennt."}
    raise HTTPException(status_code=400, detail="Ungültige Plattform")

class UploadSecretRequest(BaseModel):
    client_secret_json: str

@app.post("/api/auth/youtube/upload-secret")
async def upload_youtube_secret(req: UploadSecretRequest):
    try:
        youtube_uploader.save_client_secret_json(req.client_secret_json)
        return {"status": "success", "message": "client_secret.json erfolgreich gespeichert!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ungültiges JSON-Format: {str(e)}")

@app.post("/api/auth/{platform}/manual-token")
async def save_manual_token_endpoint(platform: str, req: ManualTokenRequest):
    if platform == "youtube":
        try:
            youtube_uploader.save_client_secret_json(req.token)
            return {"status": "success", "message": "YouTube client_secret.json erfolgreich gespeichert!"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ungültige client_secret.json: {str(e)}")
    elif platform == "instagram":
        instagram_uploader.save_manual_token(req.token, req.user_id or "")
        return {"status": "success", "message": "Instagram Token manuell gespeichert!"}
    elif platform == "tiktok":
        tiktok_uploader.save_manual_token(req.token, req.user_id or "")
        return {"status": "success", "message": "TikTok Token manuell gespeichert!"}
    elif platform == "linkedin":
        linkedin_uploader.save_manual_token(req.token, req.user_id or "")
        return {"status": "success", "message": "LinkedIn Token manuell gespeichert!"}
    raise HTTPException(status_code=400, detail="Manuelles Token für diese Plattform nicht unterstützt.")
