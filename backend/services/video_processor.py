def hex_to_ass_color(hex_color: str) -> str:
    # Converts #RRGGBB to &H00BBGGRR
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
        return f"&H00{b}{g}{r}"
    return "&H00FFFFFF"

def build_ffmpeg_command_args(video_path: str, escaped_srt_path: str, config: dict, output_path: str, start_time: str = None, duration: str = None) -> list:
    use_master_ci = config.get("use_master_ci", True)
    
    # Defaults (Mimaros)
    primary_color = config.get("primaryColor", "#14AEEA")
    text_color = config.get("textColor", "#ffffff")
    logo_path = config.get("logoPath", None)
    logo_pos = config.get("logoPosition", "top-left")
    
    # Base ASS Styling
    ass_text_color = hex_to_ass_color(text_color)
    
    if not use_master_ci:
        # Fallback to Mimaros Minimalist
        style = "FontName=Arial,FontSize=16,PrimaryColour=&H00FFFFFF,BackColour=&H80000000,Alignment=2,Bold=-1,BorderStyle=3,Outline=0,Shadow=0,MarginV=40"
        primary_color = "#14AEEA"
        logo_path = None
    else:
        design = config.get("design", "minimalist")
        if design == "minimalist":
            style = f"FontName=Arial,FontSize=16,PrimaryColour={ass_text_color},BackColour=&H80000000,Alignment=2,Bold=-1,BorderStyle=3,Outline=0,Shadow=0,MarginV=40"
        elif design == "neon":
            style = f"FontName=Courier New,FontSize=18,PrimaryColour={ass_text_color},Alignment=2,Bold=-1,BorderStyle=1,Outline=2,Shadow=2,MarginV=40"
        else: # hormozi
            style = f"FontName=Impact,FontSize=20,PrimaryColour={ass_text_color},Alignment=2,Bold=-1,BorderStyle=1,Outline=4,Shadow=0,MarginV=40"
            
    resolution = config.get("resolution", "720p")
    if resolution == "1080p":
        vf_scale = "scale='if(gt(a,9/16),-1,1080)':'if(gt(a,9/16),1920,-1)',crop=1080:1920"
        border_thickness = 10
    else:
        vf_scale = "scale='if(gt(a,9/16),-1,720)':'if(gt(a,9/16),1280,-1)',crop=720:1280"
        border_thickness = 6

    # Start building filtergraph for video stream 0
    vf_filter = f"[0:v]{vf_scale}"
    
    if use_master_ci:
        # Add primaryColor Border
        vf_filter += f",drawbox=x=0:y=0:w=iw:h=ih:color={primary_color}:thickness={border_thickness}"
        
    vf_filter += f",subtitles='{escaped_srt_path}':force_style='{style}'"
    
    cta = config.get("cta", "none")
    cta_text = ""
    # Mimaros CI CTA Style: Mimaros Blue background
    cta_box_color = "0x14AEEA@0.9"
    if cta == "subscribe":
        cta_text = "JETZT ABONNIEREN"
    elif cta == "follow":
        cta_text = "FOLGEN FÜR MEHR"
    elif cta == "more":
        cta_text = "MEHR VIDEOS"
        
    if cta_text and use_master_ci:
        safe_cta = cta_text.replace("'", "\\'")
        enable_str = ""
        dur_val = float(duration) if duration else 0.0
        if dur_val > 3.0:
            start_cta = dur_val - 3.0
            enable_str = f":enable='between(t,{start_cta},{dur_val})'"
        # Add Mimaros CI Pill (Bottom below subtitles)
        vf_filter += f",drawtext=text='{safe_cta}':fontcolor=white:fontsize=36:font='Arial':box=1:boxcolor={cta_box_color}:boxborderw=20:x=(w-text_w)/2:y=h-150{enable_str}"
        
    watermark_text = config.get("watermark_text", "mimaros.eu").replace("'", "\\'")
    if watermark_text:
        # Watermark at the top of the screen like the preview
        vf_filter += f",drawbox=x=(iw-300)/2:y=150:w=300:h=50:color=black@0.6:t=fill"
        vf_filter += f",drawtext=text='{watermark_text}':fontcolor=white:fontsize=22:font='Arial':x=(w-text_w)/2:y=165"
        
    vf_filter += "[v_base]"
    filter_complex = vf_filter
    
    cmd = ["ffmpeg", "-y"]
    if start_time:
        cmd.extend(["-ss", str(start_time)])
    cmd.extend(["-i", video_path])
    
    if logo_path and os.path.exists(logo_path) and use_master_ci:
        cmd.extend(["-i", logo_path])
        # scale logo to 100px width
        filter_complex += ";[1:v]scale=120:-1[logo]"
        if "top" in logo_pos:
            y_pos = "40"
        else:
            y_pos = "H-h-40"
            
        if "left" in logo_pos:
            x_pos = "40"
        else:
            x_pos = "W-w-40"
            
        filter_complex += f";[v_base][logo]overlay=x={x_pos}:y={y_pos}[outv]"
        map_v = "[outv]"
    else:
        map_v = "[v_base]"
        
    if duration:
        cmd.extend(["-t", str(duration)])
        
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", map_v,
        "-map", "0:a?",
        "-c:a", "aac",
        "-c:v", "libx264",
        "-threads", "1",
        "-preset", "ultrafast",
        output_path
    ])
    
    return cmd

import os
import subprocess
import json

def generate_srt(segments: list, start_time: float, end_time: float, srt_path: str):
    """
    Generiert eine .srt Datei für den spezifischen Zeitbereich (Hook).
    Für "dynamische" Untertitel packen wir kurze Textblöcke zusammen.
    """
    def format_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    index = 1
    with open(srt_path, 'w', encoding='utf-8') as f:
        for segment in segments:
            if "words" in segment:
                chunk = []
                for word in segment["words"]:
                    w_start = word["start"]
                    w_end = word["end"]
                    w_text = word["word"].strip()
                    
                    if w_start >= start_time and w_end <= end_time:
                        chunk.append({"text": w_text, "start": w_start, "end": w_end})
                        
                        if len(chunk) >= 3:
                            rel_start = chunk[0]["start"] - start_time
                            rel_end = chunk[-1]["end"] - start_time
                            chunk_text = " ".join([w["text"] for w in chunk])
                            
                            f.write(f"{index}\n")
                            f.write(f"{format_time(rel_start)} --> {format_time(rel_end)}\n")
                            f.write(f"{chunk_text.upper()}\n\n")
                            index += 1
                            chunk = []
                
                # Write remaining words in chunk
                if chunk:
                    rel_start = chunk[0]["start"] - start_time
                    rel_end = chunk[-1]["end"] - start_time
                    chunk_text = " ".join([w["text"] for w in chunk])
                    
                    f.write(f"{index}\n")
                    f.write(f"{format_time(rel_start)} --> {format_time(rel_end)}\n")
                    f.write(f"{chunk_text.upper()}\n\n")
                    index += 1
            else:
                s_start = segment["start"]
                s_end = segment["end"]
                if s_start >= start_time and s_end <= end_time:
                    rel_start = s_start - start_time
                    rel_end = s_end - start_time
                    f.write(f"{index}\n")
                    f.write(f"{format_time(rel_start)} --> {format_time(rel_end)}\n")
                    f.write(f"{segment['text'].strip().upper()}\n\n")
                    index += 1


def process_clip(video_path: str, transcript_data: dict, start_time: float, end_time: float, output_path: str, resolution: str = "720p", subtitle_config: dict = None):
    if subtitle_config is None:
        subtitle_config = {}
    subtitle_config["resolution"] = resolution
    
    base_dir = os.path.dirname(output_path)
    os.makedirs(base_dir, exist_ok=True)
        
    srt_path = os.path.join(base_dir, f"subtitles_{os.path.basename(output_path)}.srt")
    generate_srt(transcript_data.get("segments", []), start_time, end_time, srt_path)
    escaped_srt_path = srt_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
    
    clip_duration = end_time - start_time
    command = build_ffmpeg_command_args(video_path, escaped_srt_path, subtitle_config, output_path, start_time=str(start_time), duration=str(clip_duration))
    
    print(f"Führe FFmpeg aus: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=900)
        if result.returncode != 0:
            error_msg = result.stderr[-1000:] if result.stderr and len(result.stderr) > 1000 else result.stderr
            print(f"FFmpeg Fehler: {error_msg}")
            raise RuntimeError(f"FFmpeg Fehler: {error_msg}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg hat zu lange gebraucht (Timeout).")
    finally:
        if os.path.exists(srt_path):
            try: os.remove(srt_path)
            except: pass
    
    return output_path

def generate_preview(video_path: str, output_path: str, config: dict):
    base_dir = os.path.dirname(output_path)
    os.makedirs(base_dir, exist_ok=True)
    dummy_srt_path = os.path.join(base_dir, f"dummy_{os.path.basename(output_path)}.srt")
    
    with open(dummy_srt_path, "w", encoding="utf-8") as f:
        f.write("1\\n00:00:00,000 --> 00:00:01,500\\nDEIN\\n\\n")
        f.write("2\\n00:00:01,500 --> 00:00:03,000\\nUNTERTITEL\\n\\n")
        
    escaped_srt_path = dummy_srt_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
    config["resolution"] = "720p"
    
    command = build_ffmpeg_command_args(video_path, escaped_srt_path, config, output_path, start_time="0", duration="3")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            error_msg = result.stderr[-1000:] if result.stderr and len(result.stderr) > 1000 else result.stderr
            raise RuntimeError(f"FFmpeg Error: {error_msg}")
    finally:
        if os.path.exists(dummy_srt_path):
            try: os.remove(dummy_srt_path)
            except: pass

def normalize_clip(input_path: str, output_path: str, resolution: str = "1080p"):
    """
    Normiert einen Clip strikt auf 9:16 Center-Crop, 30fps und 48000Hz Stereo Audio.
    Dies ist essenziell, damit FFmpeg xfade reibungslos funktioniert.
    """
    if resolution == "1080p":
        vf_scale = "scale='if(gt(a,9/16),-1,1080)':'if(gt(a,9/16),1920,-1)',crop=1080:1920,fps=30"
    else:
        vf_scale = "scale='if(gt(a,9/16),-1,720)':'if(gt(a,9/16),1280,-1)',crop=720:1280,fps=30"
        
    command = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", vf_scale,
        "-c:v", "libx264",
        "-threads", "1",
        "-preset", "fast",
        "-c:a", "aac",
        "-ar", "48000",
        "-ac", "2",
        output_path
    ]
    
    print(f"Normalisiere Clip: {input_path}")
    result = subprocess.run(command, capture_output=True, text=True, timeout=900)
    if result.returncode != 0:
        error_msg = result.stderr[-1000:] if result.stderr and len(result.stderr) > 1000 else result.stderr
        print(f"Fehler bei Normalisierung: {error_msg}")
        raise RuntimeError(f"FFmpeg Normalisierungsfehler: {error_msg}")
    return output_path

def get_video_duration(video_path: str) -> float:
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def stitch_clips(clip_paths: list, output_path: str):
    """
    Fügt eine Liste von bereits normalisierten Clips mit Crossfade (xfade) aneinander.
    Dauer des Crossfades: 1.0 Sekunde.
    """
    if not clip_paths:
        raise ValueError("Keine Clips zum Stitchen übergeben.")
    if len(clip_paths) == 1:
        # Nur ein Clip, kopiere ihn einfach
        subprocess.run(["ffmpeg", "-y", "-i", clip_paths[0], "-c", "copy", output_path], check=True)
        return output_path
        
    fade_duration = 1.0
    
    # Baue Input Argumente
    command = ["ffmpeg", "-y"]
    durations = []
    for clip in clip_paths:
        command.extend(["-i", clip])
        durations.append(get_video_duration(clip))
        
    filter_complex = ""
    
    # xfade offset calculations
    offsets = []
    current_offset = durations[0] - fade_duration
    offsets.append(current_offset)
    for i in range(1, len(durations) - 1):
        current_offset = current_offset + durations[i] - fade_duration
        offsets.append(current_offset)
        
    # Video Filter Graph
    if len(clip_paths) == 2:
        filter_complex += f"[0:v][1:v]xfade=transition=fade:duration={fade_duration}:offset={offsets[0]}[v_out];"
    else:
        # Chain xfade for multiple clips
        filter_complex += f"[0:v][1:v]xfade=transition=fade:duration={fade_duration}:offset={offsets[0]}[v1];"
        for i in range(1, len(clip_paths) - 1):
            next_in = f"[v{i}]"
            out_label = f"[v{i+1}]" if i < len(clip_paths) - 2 else "[v_out]"
            filter_complex += f"{next_in}[{i+1}:v]xfade=transition=fade:duration={fade_duration}:offset={offsets[i]}{out_label};"
            
    # Audio Filter Graph
    if len(clip_paths) == 2:
        filter_complex += f"[0:a][1:a]acrossfade=d={fade_duration}[a_out]"
    else:
        filter_complex += f"[0:a][1:a]acrossfade=d={fade_duration}[a1];"
        for i in range(1, len(clip_paths) - 1):
            next_in = f"[a{i}]"
            out_label = f"[a{i+1}]" if i < len(clip_paths) - 2 else "[a_out]"
            filter_complex += f"{next_in}[{i+1}:a]acrossfade=d={fade_duration}{out_label}"
            if i < len(clip_paths) - 2:
                filter_complex += ";"

    command.extend([
        "-filter_complex", filter_complex,
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "libx264",
        "-threads", "1",
        "-preset", "fast",
        "-c:a", "aac",
        output_path
    ])
    
    print("Stitche Clips zusammen mit xfade...")
    result = subprocess.run(command, capture_output=True, text=True, timeout=900)
    
    if result.returncode != 0:
        error_msg = result.stderr[-1000:] if result.stderr and len(result.stderr) > 1000 else result.stderr
        raise RuntimeError(f"FFmpeg Stitching Fehler (xfade): {error_msg}")
    return output_path

def apply_branding_and_subs(stitched_path: str, transcript_data: dict, output_path: str, subtitle_config: dict):
    base_dir = os.path.dirname(output_path)
    srt_path = os.path.join(base_dir, f"subtitles_sequence.srt")
    generate_srt(transcript_data.get("segments", []), 0.0, 9999.0, srt_path)
    escaped_srt_path = srt_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\")
    
    command = build_ffmpeg_command_args(stitched_path, escaped_srt_path, subtitle_config, output_path)
    
    print(f"Führe FFmpeg (Branding) aus: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, timeout=900)
    if result.returncode != 0:
        error_msg = result.stderr[-1000:] if result.stderr and len(result.stderr) > 1000 else result.stderr
        print(f"FFmpeg Fehler: {error_msg}")
        raise RuntimeError(f"FFmpeg Fehler: {error_msg}")
        
    if os.path.exists(srt_path):
        try: os.remove(srt_path)
        except: pass
