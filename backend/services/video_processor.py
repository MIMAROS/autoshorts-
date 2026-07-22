import os
import subprocess
import json
import uuid
import urllib.request

def ensure_fonts():
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    
    fonts = {
        "WorkSans-Bold.ttf": "https://fonts.gstatic.com/s/worksans/v24/QGY_z_wNahGAdqQ43RhVcIgYT2Xz5u32K67QBi8Jow.ttf",
        "Lato-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Bold.ttf",
        "Montserrat-Black.ttf": "https://fonts.gstatic.com/s/montserrat/v31/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCvC73w5aX8.ttf"
    }
    
    for font_name, url in fonts.items():
        font_path = os.path.join(fonts_dir, font_name)
        if not os.path.exists(font_path):
            print(f"Downloading font {font_name}...")
            try:
                urllib.request.urlretrieve(url, font_path)
            except Exception as e:
                print(f"Error downloading {font_name}: {e}")
    return fonts_dir

def generate_cta_button_image(text: str, bg_color_hex: str, text_color_hex: str, font_name: str, resolution: str, output_path: str) -> str:
    from PIL import Image, ImageDraw, ImageFont
    
    # Setup dimensions based on resolution
    if resolution == "1080p":
        font_size = 64
        padding_x = 90
        padding_y = 35
        radius = 45
    else: # 720p / preview
        font_size = 42
        padding_x = 60
        padding_y = 25
        radius = 30
        
    # Get the font
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
    if font_name == "Work Sans":
        font_file = "WorkSans-Bold.ttf"
    elif font_name == "Montserrat":
        font_file = "Montserrat-Black.ttf"
    else:
        font_file = "Lato-Bold.ttf"
    font_path = os.path.join(fonts_dir, font_file)
    if not os.path.exists(font_path):
        ensure_fonts()
    if not os.path.exists(font_path):
        font_path = "arial.ttf" # system fallback
        
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()
        
    # Measure text precisely
    try:
        left, top, right, bottom = font.getbbox(text)
        text_width = right - left
        text_height = bottom - top
    except:
        text_width = len(text) * int(font_size * 0.6)
        text_height = font_size
        
    width = text_width + (padding_x * 2)
    height = text_height + (padding_y * 2)
    
    # Create transparent image
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw rounded rectangle
    draw.rounded_rectangle(
        [(0, 0), (width, height)],
        radius=radius,
        fill=bg_color_hex
    )
    
    # Draw text centered precisely
    try:
        draw.text((width / 2, height / 2), text, fill=text_color_hex, font=font, anchor="mm")
    except:
        draw.text((padding_x, padding_y), text, fill=text_color_hex, font=font)
        
    # Save to path
    image.save(output_path, "PNG")
    return output_path

def hex_to_ass_color(hex_color: str) -> str:
    # Converts #RRGGBB to &H00BBGGRR
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
        return f"&H00{b}{g}{r}"
    return "&H00FFFFFF"

def build_ffmpeg_command_args(video_path: str, escaped_srt_path: str, config: dict, output_path: str, start_time: str = None, duration: str = None) -> list:
    use_master_ci = config.get("use_master_ci", True)
    
    # Fonts download & path
    fonts_dir = ensure_fonts()
    escaped_fonts_dir = fonts_dir.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")

    # Defaults (Mimaros)
    primary_color = config.get("primaryColor", "#14AEEA")
    text_color = config.get("textColor", "#ffffff")
    logo_path = config.get("logoPath", None)
    logo_pos = str(config.get("logoPosition", "top-left")).lower().replace("-", "_")
    font_name = config.get("fontName", "Work Sans")
    
    # Base ASS Styling
    ass_text_color = hex_to_ass_color(text_color)
    
    # Mapping selected font names to families registered in TTF files
    if font_name == "Work Sans":
        ass_font = "Work Sans"
    elif font_name == "Lato":
        ass_font = "Lato"
    elif font_name == "Montserrat":
        ass_font = "Montserrat"
    else:
        ass_font = "Impact"
        
    if not use_master_ci:
        # Fallback to Mimaros Minimalist
        style = f"FontName={ass_font},FontSize=12,PrimaryColour=&H00FFFFFF,BackColour=&H80000000,Alignment=2,Bold=-1,BorderStyle=3,Outline=0,Shadow=0,MarginV=40"
        primary_color = "#14AEEA"
        logo_path = None
    else:
        design = config.get("design", "minimalist")
        if design == "minimalist":
            style = f"FontName={ass_font},FontSize=15,PrimaryColour={ass_text_color},BackColour=&H80000000,Alignment=2,Bold=-1,BorderStyle=3,Outline=0,Shadow=0,MarginV=60"
        elif design == "neon":
            style = f"FontName={ass_font},FontSize=17,PrimaryColour={ass_text_color},Alignment=2,Bold=-1,BorderStyle=1,Outline=3,Shadow=3,MarginV=60"
        else: # hormozi
            style = f"FontName={ass_font},FontSize=20,PrimaryColour={ass_text_color},Alignment=2,Bold=-1,BorderStyle=1,Outline=5,Shadow=0,MarginV=60"
            
    resolution = config.get("resolution", "720p")
    if resolution == "1080p":
        vf_scale = "scale='if(gt(a,9/16),-1,1080)':'if(gt(a,9/16),1920,-1)',crop=1080:1920"
        border_thickness = 10
        logo_width = 180
        margin_x, margin_y = 60, 60
        cta_offset_y = 280
    else:
        vf_scale = "scale='if(gt(a,9/16),-1,720)':'if(gt(a,9/16),1280,-1)',crop=720:1280"
        border_thickness = 6
        logo_width = 120
        margin_x, margin_y = 40, 40
        cta_offset_y = 200

    # Start building filtergraph for video stream 0
    vf_filter = f"[0:v]{vf_scale}"
    
    if use_master_ci:
        # Add primaryColor Border
        vf_filter += f",drawbox=x=0:y=0:w=iw:h=ih:color={primary_color}:thickness={border_thickness}"
        
    vf_filter += f",subtitles='{escaped_srt_path}':fontsdir='{escaped_fonts_dir}':force_style='{style}'"
    
    # Watermark
    watermark_text = config.get("watermark_text", "mimaros.eu").replace("'", "\\'")
    if watermark_text:
        # Watermark at the top of the screen like the preview
        vf_filter += f",drawbox=x=(iw-300)/2:y=150:w=300:h=50:color=black@0.6:t=fill"
        vf_filter += f",drawtext=text='{watermark_text}':fontcolor=white:fontsize=22:font='{ass_font}':x=(w-text_w)/2:y=165"
        
    vf_filter += "[v_base]"
    filter_complex = vf_filter
    
    # Compose input files
    inputs = [video_path]
    
    # 1. Overlay Logo
    logo_input_index = -1
    if logo_path and os.path.exists(logo_path) and use_master_ci:
        inputs.append(logo_path)
        logo_input_index = len(inputs) - 1
        
        # Coordinates calculation basierend auf selected position
        if "top" in logo_pos:
            y_pos = f"{margin_y}"
        elif "bottom" in logo_pos:
            y_pos = f"H-h-{margin_y}"
        else:
            y_pos = f"{margin_y}"
            
        if "left" in logo_pos:
            x_pos = f"{margin_x}"
        elif "right" in logo_pos:
            x_pos = f"W-w-{margin_x}"
        elif "center" in logo_pos or "middle" in logo_pos:
            x_pos = f"(W-w)/2"
        else:
            x_pos = f"{margin_x}"
            
        filter_complex += f";[{logo_input_index}:v]scale={logo_width}:-1[logo];[v_base][logo]overlay=x={x_pos}:y={y_pos}[v_logo]"
        current_v = "[v_logo]"
    else:
        current_v = "[v_base]"
        
    # 2. Overlay CTA Button
    cta = config.get("cta", "none")
    cta_text = ""
    if cta == "subscribe":
        cta_text = "JETZT ABONNIEREN"
    elif cta == "follow":
        cta_text = "FOLGEN FÜR MEHR"
    elif cta == "more":
        cta_text = "MEHR VIDEOS"
        
    cta_input_index = -1
    if cta_text and use_master_ci:
        # Generate rounded button image dynamically
        cta_img_path = os.path.join(os.path.dirname(output_path), f"cta_{os.path.basename(output_path)}.png")
        try:
            generate_cta_button_image(cta_text, primary_color, "#FFFFFF", font_name, resolution, cta_img_path)
            inputs.append(cta_img_path)
            cta_input_index = len(inputs) - 1
            
            # Setup fade timing (CTA visible in last 3s)
            dur_val = float(duration) if duration else 0.0
            if dur_val > 3.0:
                start_cta = dur_val - 3.0
                enable_str = f":enable='between(t,{start_cta},{dur_val})'"
            else:
                enable_str = ""
                
            filter_complex += f";{current_v}[{cta_input_index}:v]overlay=x=(W-w)/2:y=H-{cta_offset_y}{enable_str}[v_cta]"
            current_v = "[v_cta]"
        except Exception as e:
            print(f"Error generating CTA image button: {e}")
            
    map_v = current_v
    
    # Build actual ffmpeg command
    cmd = ["ffmpeg", "-y"]
    for i, path in enumerate(inputs):
        if i == 0:
            if start_time and path != "demo":
                cmd.extend(["-ss", str(start_time)])
            if path == "demo":
                if resolution == "1080p":
                    cmd.extend(["-f", "lavfi", "-i", "color=c=0x151515:s=1080x1920:r=30"])
                else:
                    cmd.extend(["-f", "lavfi", "-i", "color=c=0x151515:s=720x1280:r=30"])
            else:
                cmd.extend(["-i", path])
        else:
            cmd.extend(["-i", path])
            
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

def generate_srt(segments: list, start_time: float, end_time: float, srt_path: str, config: dict = None):
    """
    Generiert eine .srt Datei für den spezifischen Zeitbereich (Hook) mit Karaoke-Word-Highlighting.
    """
    if config is None:
        config = {}
    highlight_color = config.get("highlightColor", "#C89B31")
    
    def format_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    index = 1
    with open(srt_path, 'w', encoding='utf-8') as f:
        for segment in segments:
            if "words" in segment and segment["words"]:
                # Filter words that fall in the clip range
                words_in_range = []
                for word in segment["words"]:
                    w_start = word["start"]
                    w_end = word["end"]
                    w_text = word["word"].strip()
                    if w_start >= start_time and w_end <= end_time:
                        words_in_range.append({"text": w_text, "start": w_start, "end": w_end})
                
                if not words_in_range:
                    continue
                
                # Group words in chunks of 3 (or 2-4 words)
                chunk_size = 3
                for chunk_idx in range(0, len(words_in_range), chunk_size):
                    chunk = words_in_range[chunk_idx : chunk_idx + chunk_size]
                    if not chunk:
                        continue
                    
                    chunk_start = chunk[0]["start"] - start_time
                    chunk_end = chunk[-1]["end"] - start_time
                    
                    # Write an event for each word in the chunk, highlighting it
                    for i, active_word in enumerate(chunk):
                        # Determine event start and end times to avoid gaps
                        if i == 0:
                            event_start = chunk_start
                        else:
                            event_start = chunk[i]["start"] - start_time
                            
                        if i == len(chunk) - 1:
                            event_end = chunk_end
                        else:
                            event_end = chunk[i+1]["start"] - start_time
                            
                        # Build text with highlighted active word
                        formatted_words = []
                        for j, w in enumerate(chunk):
                            w_text = w["text"].upper()
                            if j == i:
                                formatted_words.append(f'<font color="{highlight_color}">{w_text}</font>')
                            else:
                                formatted_words.append(w_text)
                                
                        chunk_text = " ".join(formatted_words)
                        
                        # Write SRT block
                        f.write(f"{index}\n")
                        f.write(f"{format_time(event_start)} --> {format_time(event_end)}\n")
                        f.write(f"{chunk_text}\n\n")
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
    generate_srt(transcript_data.get("segments", []), start_time, end_time, srt_path, subtitle_config)
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
        cta_img_path = os.path.join(os.path.dirname(output_path), f"cta_{os.path.basename(output_path)}.png")
        if os.path.exists(cta_img_path):
            try: os.remove(cta_img_path)
            except: pass
    
    return output_path

def generate_preview(video_path: str, output_path: str, config: dict):
    base_dir = os.path.dirname(output_path)
    os.makedirs(base_dir, exist_ok=True)
    dummy_srt_path = os.path.join(base_dir, f"dummy_{os.path.basename(output_path)}.srt")
    
    highlight = config.get("highlightColor", "#C89B31")
    with open(dummy_srt_path, "w", encoding="utf-8") as f:
        f.write(f"1\n00:00:00,000 --> 00:00:01,000\n<font color=\"{highlight}\">DEIN</font> UNTERTITEL VORSCHAU\n\n")
        f.write(f"2\n00:00:01,000 --> 00:00:02,000\nDEIN <font color=\"{highlight}\">UNTERTITEL</font> VORSCHAU\n\n")
        f.write(f"3\n00:00:02,000 --> 00:00:03,000\nDEIN UNTERTITEL <font color=\"{highlight}\">VORSCHAU</font>\n\n")
        
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
        cta_img_path = os.path.join(os.path.dirname(output_path), f"cta_{os.path.basename(output_path)}.png")
        if os.path.exists(cta_img_path):
            try: os.remove(cta_img_path)
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
    generate_srt(transcript_data.get("segments", []), 0.0, 9999.0, srt_path, subtitle_config)
    escaped_srt_path = srt_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\")
    
    command = build_ffmpeg_command_args(stitched_path, escaped_srt_path, subtitle_config, output_path)
    
    print(f"Führe FFmpeg (Branding) aus: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=900)
        if result.returncode != 0:
            error_msg = result.stderr[-1000:] if result.stderr and len(result.stderr) > 1000 else result.stderr
            print(f"FFmpeg Fehler: {error_msg}")
            raise RuntimeError(f"FFmpeg Fehler: {error_msg}")
    finally:
        if os.path.exists(srt_path):
            try: os.remove(srt_path)
            except: pass
        cta_img_path = os.path.join(os.path.dirname(output_path), f"cta_{os.path.basename(output_path)}.png")
        if os.path.exists(cta_img_path):
            try: os.remove(cta_img_path)
            except: pass
