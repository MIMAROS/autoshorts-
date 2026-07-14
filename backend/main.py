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
from services import youtube_uploader
from services.supabase_client import upload_file_to_supabase

app = FastAPI(title="YouTube to Shorts AI Automation API")

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
                if not s.get("uploaded") and "YouTube Shorts" in s.get("platforms", []):
                    # parse YYYY-MM-DD HH:MM
                    try:
                        scheduled_time = datetime.strptime(s["schedule_date"], "%Y-%m-%d %H:%M")
                        if now >= scheduled_time:
                            print(f"Uploading scheduled video: {s['video_url']}")
                            
                            # Wandle URL in lokalen Dateipfad um
                            # video_url is like http://127.0.0.1:8000/videos/job_123_clip.mp4
                            # local path is in Fertige_Shorts/job_123_clip.mp4
                            filename = s["video_url"].split("/videos/")[-1]
                            local_path = os.path.join(export_dir, filename)
                            
                            if os.path.exists(local_path):
                                if youtube_uploader.is_authenticated():
                                    youtube_uploader.upload_short(local_path, s.get("caption", "AutoShorts Video"), s.get("caption", ""), "private")
                                    s["uploaded"] = True
                                    print("Upload successful!")
                                else:
                                    print("YouTube is not authenticated. Skipping upload.")
                            else:
                                print(f"File not found: {local_path}")
                                s["uploaded"] = True # mark as uploaded to avoid infinite retry
                    except ValueError:
                        pass
        except Exception as e:
            print(f"Error in background uploader: {e}")
        
        await asyncio.sleep(60)

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
            if trim_start is not None and trim_end is not None:
                # Trimming local file with FFmpeg
                import subprocess
                trimmed_path = os.path.join("temp", f"{job_id}_trimmed.mp4")
                duration = trim_end - trim_start
                try:
                    subprocess.run(["ffmpeg", "-y", "-i", local_path, "-ss", str(trim_start), "-t", str(duration), "-c", "copy", trimmed_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    video_path = trimmed_path
                except Exception as e:
                    print(f"Fehler beim lokalen Trimming: {e}")
                    video_path = local_path
            else:
                video_path = local_path
        else:
            video_path = download_video(url, output_path=f"temp/{job_id}", trim_start=trim_start, trim_end=trim_end)
        
        # 2. Transkribieren
        jobs[job_id] = {"status": "transcribing", "progress": 40, "hooks": [], "clips": []}
        transcript_data = transcribe_audio(video_path, video_lang, subtitle_lang)
        
        # 3. KI Analyse mit Gemini
        jobs[job_id] = {"status": "analyzing", "progress": 70, "hooks": [], "clips": []}
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
        
        jobs[job_id] = {"status": "done", "progress": 100, "hooks": hooks, "clips": clips}
        
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

@app.post("/api/video-info")
async def video_info(request: VideoInfoRequest):
    if not request.youtube_url:
        raise HTTPException(status_code=400, detail="YouTube URL is required")
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
    
    # Save file
    file_path = os.path.join(temp_dir, f"logo_{uuid.uuid4().hex[:8]}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    return {
        "status": "success",
        "logo_path": file_path
    }

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
        abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp", "demo.mp4")
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

@app.get("/api/auth/status")
async def auth_status():
    """
    Returns the auth status for all platforms.
    """
    youtube_connected = youtube_uploader.is_authenticated()
    return {
        "youtube": youtube_connected,
        "tiktok": False
    }

@app.post("/api/auth/{platform}")
async def auth_platform(platform: str):
    """
    Initiates OAuth flow.
    """
    if platform == "youtube":
        # Redirect URI für den Callback
        redirect_uri = "http://localhost:3000/api/auth/youtube/callback" # We'll handle this in Next.js later or direct to backend
        # Let's direct to backend callback directly to keep it simple:
        redirect_uri = "http://127.0.0.1:8000/api/auth/youtube/callback"
        
        auth_url, _ = youtube_uploader.get_auth_url(redirect_uri)
        if not auth_url:
            raise HTTPException(status_code=400, detail="client_secret.json is missing. Please download it from Google Cloud Console.")
        return {"auth_url": auth_url}
    
    raise HTTPException(status_code=400, detail="Invalid or unsupported platform")

@app.get("/api/auth/youtube/callback")
async def youtube_auth_callback(code: str):
    """
    Handles the Google OAuth redirect.
    """
    redirect_uri = "http://127.0.0.1:8000/api/auth/youtube/callback"
    try:
        youtube_uploader.fetch_token_from_code(code, redirect_uri)
        # Redirect back to frontend
        return RedirectResponse(url="http://localhost:3000/")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
