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
        "Montserrat-Black.ttf": "https://fonts.gstatic.com/s/montserrat/v31/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCvC73w5aX8.ttf",
        "Oswald-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/oswald/Oswald-Bold.ttf",
        "Anton-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf"
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
    elif font_name == "Oswald":
        font_file = "Oswald-Bold.ttf"
    elif font_name == "Anton":
        font_file = "Anton-Regular.ttf"
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

def get_font_file_path(font_name: str, fonts_dir: str) -> str:
    if font_name == "Work Sans":
        return os.path.join(fonts_dir, "WorkSans-Bold.ttf")
    elif font_name == "Montserrat":
        return os.path.join(fonts_dir, "Montserrat-Black.ttf")
    elif font_name == "Oswald":
        return os.path.join(fonts_dir, "Oswald-Bold.ttf")
    elif font_name == "Anton":
        return os.path.join(fonts_dir, "Anton-Regular.ttf")
    elif font_name == "Lato":
        return os.path.join(fonts_dir, "Lato-Bold.ttf")
    elif font_name == "Impact":
        return os.path.join(fonts_dir, "Impact-Regular.ttf")
    return os.path.join(fonts_dir, "WorkSans-Bold.ttf")

def build_ffmpeg_command_args(video_path: str, escaped_srt_path: str, config: dict, output_path: str, start_time: str = None, duration: str = None) -> list:
    use_master_ci = config.get("use_master_ci", True)
    
    # Read Visibility Toggles (default to True)
    show_title = config.get("showTitle", True)
    show_logo = config.get("showLogo", True)
    show_subtitles = config.get("showSubtitles", True)
    show_cta = config.get("showCTA", True)
    
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
        
    hook_header = config.get("hookHeader", "").strip().replace("'", "\\'")
    has_title = bool(hook_header and show_title)
    
    resolution = config.get("resolution", "720p")
    if resolution == "1080p":
        ass_margin_v = 480
        ass_margin_lr = 120
        vf_scale = "scale='if(gt(a,9/16),-1,1080)':'if(gt(a,9/16),1920,-1)',crop=1080:1920"
        border_thickness = 10
        logo_width = 180
        margin_x = 60
        margin_y = 30 # Logo is at the very top
        cta_offset_y = 170
    else:
        ass_margin_v = 320
        ass_margin_lr = 80
        vf_scale = "scale='if(gt(a,9/16),-1,720)':'if(gt(a,9/16),1280,-1)',crop=720:1280"
        border_thickness = 6
        logo_width = 120
        margin_x = 40
        margin_y = 20 # Logo is at the very top
        cta_offset_y = 113

    # Start building filtergraph for video stream 0
    vf_filter = f"[0:v]{vf_scale}"
    
    if use_master_ci:
        # Add primaryColor Border
        vf_filter += f",drawbox=x=0:y=0:w=iw:h=ih:color={primary_color}:thickness={border_thickness}"
        
        # 4. Top Video Title (styled with bounding box backdrop exactly like subtitles, placed below logo)
        if has_title:
            font_path = get_font_file_path(font_name, fonts_dir).replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
            has_top_logo = show_logo and logo_path and os.path.exists(logo_path) and ("top" in logo_pos)
            
            if has_top_logo:
                title_y = 240 if resolution == "1080p" else 160
            else:
                title_y = 50 if resolution == "1080p" else 30
                
            if resolution == "1080p":
                title_font_size = 80
                box_border_w = 20
            else:
                title_font_size = 54
                box_border_w = 12
                
            # Draw title with 70% opacity Deep Blue backdrop box using box border padding
            vf_filter += f",drawtext=text='{hook_header.upper()}':fontfile='{font_path}':fontsize={title_font_size}:fontcolor=white:box=1:boxcolor=0x0B192C@0.7:boxborderw={box_border_w}:x=(w-text_w)/2:y={title_y}"
            
        # 5. Full-Width Subtitle Backdrop Banner (extends all the way to the bottom border)
        if show_subtitles:
            if resolution == "1080p":
                vf_filter += f",drawbox=x=0:y=1320:w=iw:h=ih-1320:color=0x0B192C@0.7:t=fill"
            else:
                vf_filter += f",drawbox=x=0:y=880:w=iw:h=ih-880:color=0x0B192C@0.7:t=fill"
        
    if show_subtitles:
        vf_filter += f",subtitles='{escaped_srt_path}':fontsdir='{escaped_fonts_dir}'"
    
    # Watermark
    watermark_text = config.get("watermark_text", "mimaros.eu").replace("'", "\\'")
    if watermark_text:
        # Watermark position shifted if top title is present to avoid overlay
        if has_title:
            watermark_y = 380 if resolution == "1080p" else 250
        else:
            watermark_y = 30 if resolution == "1080p" else 20
            
        vf_filter += f",drawbox=x=(iw-300)/2:y={watermark_y}:w=300:h=50:color=black@0.6:t=fill"
        vf_filter += f",drawtext=text='{watermark_text}':fontcolor=white:fontsize=22:font='{ass_font}':x=(w-text_w)/2:y={watermark_y+15}"
        
    vf_filter += "[v_base]"
    filter_complex = vf_filter
    
    # Compose input files
    inputs = [video_path]
    
    # 1. Overlay Logo
    logo_input_index = -1
    if logo_path and os.path.exists(logo_path) and use_master_ci and show_logo:
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
    if cta_text and use_master_ci and show_cta:
        # Generate rounded button image dynamically
        cta_img_path = os.path.join(os.path.dirname(output_path), f"cta_{os.path.basename(output_path)}.png")
        try:
            generate_cta_button_image(cta_text, primary_color, "#FFFFFF", font_name, resolution, cta_img_path)
            inputs.append(cta_img_path)
            cta_input_index = len(inputs) - 1
            
            # Setup dynamic intervals
            dur_val = float(duration) if duration else 0.0
            intervals = []
            if dur_val > 0.0:
                half_time = dur_val / 2.0
                # Trigger 1: at 50% for 4 seconds
                intervals.append((half_time, min(half_time + 4.0, dur_val)))
                
                # Intervall-Option: if video > 45s, show every 30s for 4s
                if dur_val > 45.0:
                    t = 30.0
                    while t < dur_val:
                        # avoid overlaps with Trigger 1
                        if not (t >= half_time - 4.0 and t <= half_time + 4.0):
                            intervals.append((t, min(t + 4.0, dur_val)))
                        t += 30.0
            
            if intervals:
                enable_expr = "+".join([f"between(t,{start},{end})" for start, end in intervals])
                
                # Build fade chain for looped stream
                fade_chain = f"[{cta_input_index}:v]loop=loop=-1:size=1:start=0,setpts=PTS-STARTPTS"
                for start, end in intervals:
                    # Fade in for 0.5s, fade out for 0.5s
                    fade_chain += f",fade=t=in:st={start}:d=0.5:alpha=1,fade=t=out:st={end-0.5}:d=0.5:alpha=1"
                fade_chain += "[cta_faded]"
                
                filter_complex += f";{fade_chain};{current_v}[cta_faded]overlay=x=(W-w)/2:y=(H-h)/2:enable='{enable_expr}'[v_cta]"
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
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-threads", "1",
        "-preset", "ultrafast",
        output_path
    ])
    
    return cmd

def generate_ass(segments: list, start_time: float, end_time: float, ass_path: str, config: dict = None):
    """
    Generiert eine .ass Datei für den spezifischen Zeitbereich (Hook) mit 5 stark abweichenden
    Untertitel-Vorlagen (Karaoke, Dynamic Box, Pop-Up Bouncy, Hormozi, mimaros Clean).
    """
    if config is None:
        config = {}
    
    # Read styling parameters
    highlight_color_hex = config.get("highlightColor", "#D4AF37").lstrip('#')
    text_color_hex = config.get("textColor", "#ffffff").lstrip('#')
    primary_color_hex = config.get("primaryColor", "#14AEEA").lstrip('#')
    
    # Convert hex colors to ASS format (AABBGGRR)
    if len(highlight_color_hex) == 6:
        h_r, h_g, h_b = highlight_color_hex[0:2], highlight_color_hex[2:4], highlight_color_hex[4:6]
        highlight_color_ass = f"&H00{h_b}{h_g}{h_r}&" # inline tag
        highlight_color_style = f"&H00{h_b}{h_g}{h_r}" # style line
    else:
        highlight_color_ass = "&H0037AFD4&"
        highlight_color_style = "&H0037AFD4"
        
    if len(text_color_hex) == 6:
        t_r, t_g, t_b = text_color_hex[0:2], text_color_hex[2:4], text_color_hex[4:6]
        text_color_ass = f"&H00{t_b}{t_g}{t_r}"
    else:
        text_color_ass = "&H00FFFFFF"
        
    if len(primary_color_hex) == 6:
        p_r, p_g, p_b = primary_color_hex[0:2], primary_color_hex[2:4], primary_color_hex[4:6]
        primary_color_box_ass = f"&H4C{p_b}{p_g}{p_r}" # 70% opacity Deep Blue/CI Color
    else:
        primary_color_box_ass = "&H4C0B192C" # fallback Deep Blue
        
    font_name = config.get("fontName", "Work Sans")
    ass_font = "Work Sans"
    if font_name == "Lato":
        ass_font = "Lato"
    elif font_name == "Montserrat":
        ass_font = "Montserrat"
    elif font_name == "Oswald":
        ass_font = "Oswald"
    elif font_name == "Anton":
        ass_font = "Anton"
    elif font_name == "Impact":
        ass_font = "Impact"
        
    # Margin settings based on resolution
    resolution = config.get("resolution", "720p")
    if resolution == "1080p":
        ass_margin_v = 480
        ass_margin_lr = 120
        font_size = 76
        active_font_size = 86
        title_font_size = 80
        title_margin_v = 40
    else:
        ass_margin_v = 320
        ass_margin_lr = 80
        font_size = 50
        active_font_size = 56
        title_font_size = 54
        title_margin_v = 25
        
    def format_ass_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centis = int(round((seconds % 1) * 100))
        if centis >= 100:
            secs += 1
            centis = 0
        return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

    design = config.get("design", "karaoke")
    print(f"Generating ASS subtitles with template: {design} to path: {ass_path}")
    try:
        with open(ass_path, 'w', encoding='utf-8') as f:
            # 1. Write ASS Header
            f.write("[Script Info]\n")
            f.write("ScriptType: v4.00+\n")
            f.write("PlayResX: 1080\n" if resolution == "1080p" else "PlayResX: 720\n")
            f.write("PlayResY: 1920\n" if resolution == "1080p" else "PlayResY: 1280\n")
            f.write("ScaledBorderAndShadow: yes\n\n")
            
            # 2. Write Styles
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            
            # Apply individual style parameters based on template choice
            if design == "dynamic_box":
                # Outline is 0, Box border is drawn using BorderStyle=3 with 70% opacity CI primary color box
                f.write(f"Style: Default,{ass_font},{font_size},{text_color_ass},&H000000FF,&H00000000,{primary_color_box_ass},-1,0,0,0,100,100,0,0,3,0,0,2,{ass_margin_lr},{ass_margin_lr},{ass_margin_v},1\n")
            elif design == "popup_bouncy":
                # Centered exactly in the middle of the screen (Alignment=5)
                f.write(f"Style: Default,{ass_font},{font_size},{text_color_ass},&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,0,5,{ass_margin_lr},{ass_margin_lr},{ass_margin_v},1\n")
            elif design == "hormozi":
                # Ultra thick Anton font by default, bold outline
                f.write(f"Style: Default,Anton,{font_size + 6},{text_color_ass},&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,0,2,{ass_margin_lr},{ass_margin_lr},{ass_margin_v},1\n")
            elif design == "mimaros_clean":
                # Thin, elegant Montserrat/Work Sans, smaller, alignment bottom center
                f.write(f"Style: Default,{ass_font},{font_size - 4},{text_color_ass},&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1.5,0,2,{ass_margin_lr},{ass_margin_lr},{ass_margin_v},1\n")
            else: # karaoke highlight (default)
                f.write(f"Style: Default,{ass_font},{font_size},{text_color_ass},&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,0,2,{ass_margin_lr},{ass_margin_lr},{ass_margin_v},1\n")
            
            f.write("\n")
            
            # 3. Write Events
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            
            # Write Subtitle segments
            index = 1
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
                    
                    # Set chunk size based on template
                    if design == "popup_bouncy":
                        chunk_size = 1 # 1 word at a time
                    elif design == "hormozi":
                        chunk_size = 2 # max 2 words per line
                    elif design == "mimaros_clean":
                        chunk_size = 6 # whole elegant sentences
                    else: # karaoke / dynamic_box
                        chunk_size = 3
                        
                    for chunk_idx in range(0, len(words_in_range), chunk_size):
                        chunk = words_in_range[chunk_idx : chunk_idx + chunk_size]
                        if not chunk:
                            continue
                        
                        chunk_start = chunk[0]["start"] - start_time
                        chunk_end = chunk[-1]["end"] - start_time
                        
                        # Write an event for each word in the chunk, highlighting it
                        for i, active_word in enumerate(chunk):
                            if i == 0:
                                event_start = chunk_start
                            else:
                                event_start = chunk[i]["start"] - start_time
                                
                            if i == len(chunk) - 1:
                                event_end = chunk_end
                            else:
                                event_end = chunk[i+1]["start"] - start_time
                                
                            # Build text with custom formatting per design template
                            formatted_words = []
                            for j, w in enumerate(chunk):
                                w_text = w["text"].upper()
                                
                                if design == "mimaros_clean":
                                    # No active highlight, clean sentences fade in gently
                                    formatted_words.append(w_text)
                                elif design == "hormozi":
                                    # Yellow/Green alternating highlights
                                    if j == i:
                                        hormozi_color = "&H0000FFFF&" if i % 2 == 0 else "&H0000FF00&" # yellow or green
                                        formatted_words.append(f"{{\\c{hormozi_color}\\fs{active_font_size + 4}}}{w_text}{{\\rDefault}}")
                                    else:
                                        formatted_words.append(w_text)
                                elif design == "popup_bouncy":
                                    # Single bouncy word center
                                    formatted_words.append(f"{{\\fs{active_font_size + 10}}}{w_text}{{\\rDefault}}")
                                elif design == "dynamic_box":
                                    # Bounding box is drawn behind active word or sentence. Text remains white.
                                    # We can highlight active word color or keep all white inside the box
                                    if j == i:
                                        formatted_words.append(f"{{\\c{highlight_color_ass}\\fs{active_font_size}}}{w_text}{{\\rDefault}}")
                                    else:
                                        formatted_words.append(w_text)
                                else: # karaoke highlight
                                    if j == i:
                                        formatted_words.append(f"{{\\c{highlight_color_ass}\\fs{active_font_size}}}{w_text}{{\\rDefault}}")
                                    else:
                                        formatted_words.append(w_text)
                                        
                            chunk_text = " ".join(formatted_words)
                            
                            # Add fade effect to mimaros_clean template
                            if design == "mimaros_clean" and i == 0:
                                chunk_text = f"{{\\fad(250,250)}}{chunk_text}"
                                
                            f.write(f"Dialogue: 0,{format_ass_time(event_start)},{format_ass_time(event_end)},Default,,0,0,0,,{chunk_text}\n")
                            index += 1
                else:
                    s_start = segment["start"]
                    s_end = segment["end"]
                    if s_start >= start_time and s_end <= end_time:
                        rel_start = s_start - start_time
                        rel_end = s_end - start_time
                        # Default fade for B2B template
                        effect = "{\\fad(250,250)}" if design == "mimaros_clean" else ""
                        f.write(f"Dialogue: 0,{format_ass_time(rel_start)},{format_ass_time(rel_end)},Default,,0,0,0,,{effect}{segment['text'].strip().upper()}\n")
                        index += 1
        print(f"ASS subtitles successfully created at {ass_path}")
    except Exception as e:
        print(f"Failed to generate ASS file: {e}")
        raise e

def process_clip(video_path: str, transcript_data: dict, start_time: float, end_time: float, output_path: str, resolution: str = "720p", subtitle_config: dict = None):
    if subtitle_config is None:
        subtitle_config = {}
    subtitle_config["resolution"] = resolution
    
    base_dir = os.path.dirname(output_path)
    os.makedirs(base_dir, exist_ok=True)
        
    ass_path = os.path.join(base_dir, f"subtitles_{os.path.basename(output_path)}.ass")
    generate_ass(transcript_data.get("segments", []), start_time, end_time, ass_path, subtitle_config)
    escaped_ass_path = ass_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
    
    clip_duration = end_time - start_time
    command = build_ffmpeg_command_args(video_path, escaped_ass_path, subtitle_config, output_path, start_time=str(start_time), duration=str(clip_duration))
    
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
        if os.path.exists(ass_path):
            try: os.remove(ass_path)
            except: pass
        cta_img_path = os.path.join(os.path.dirname(output_path), f"cta_{os.path.basename(output_path)}.png")
        if os.path.exists(cta_img_path):
            try: os.remove(cta_img_path)
            except: pass

def generate_preview(video_path: str, output_path: str, config: dict):
    base_dir = os.path.dirname(output_path)
    os.makedirs(base_dir, exist_ok=True)
    dummy_ass_path = os.path.join(base_dir, f"dummy_{os.path.basename(output_path)}.ass")
    
    # Mock segment with word timestamps for full preview emulation
    mock_segments = [
        {
            "start": 0.0,
            "end": 3.0,
            "text": "DEIN UNTERTITEL VORSCHAU",
            "words": [
                {"word": "DEIN", "start": 0.0, "end": 1.0},
                {"word": "UNTERTITEL", "start": 1.0, "end": 2.0},
                {"word": "VORSCHAU", "start": 2.0, "end": 3.0}
            ]
        }
    ]
    
    generate_ass(mock_segments, 0.0, 3.0, dummy_ass_path, config)
    escaped_ass_path = dummy_ass_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
    config["resolution"] = "720p"
    
    command = build_ffmpeg_command_args(video_path, escaped_ass_path, config, output_path, start_time="0", duration="3")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            error_msg = result.stderr[-1000:] if result.stderr and len(result.stderr) > 1000 else result.stderr
            raise RuntimeError(f"FFmpeg Error: {error_msg}")
    finally:
        if os.path.exists(dummy_ass_path):
            try: os.remove(dummy_ass_path)
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
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
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
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
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
    ass_path = os.path.join(base_dir, f"subtitles_sequence.ass")
    generate_ass(transcript_data.get("segments", []), 0.0, 9999.0, ass_path, subtitle_config)
    escaped_ass_path = ass_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\")
    
    command = build_ffmpeg_command_args(stitched_path, escaped_ass_path, subtitle_config, output_path)
    
    print(f"Führe FFmpeg (Branding) aus: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=900)
        if result.returncode != 0:
            error_msg = result.stderr[-1000:] if result.stderr and len(result.stderr) > 1000 else result.stderr
            print(f"FFmpeg Fehler: {error_msg}")
            raise RuntimeError(f"FFmpeg Fehler: {error_msg}")
    finally:
        if os.path.exists(ass_path):
            try: os.remove(ass_path)
            except: pass
        cta_img_path = os.path.join(os.path.dirname(output_path), f"cta_{os.path.basename(output_path)}.png")
        if os.path.exists(cta_img_path):
            try: os.remove(cta_img_path)
            except: pass
