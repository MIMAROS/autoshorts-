import os
import subprocess
import json
import uuid
import urllib.request

def ensure_fonts():
    """
    Returns the permanent backend/assets/fonts directory containing all high-resolution TTF font families.
    """
    local_fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")
    os.makedirs(local_fonts_dir, exist_ok=True)
    return local_fonts_dir

def get_font_file_path(font_name: str, fonts_dir: str = None) -> str:
    """
    Returns the absolute path to the TTF font file.
    """
    if not fonts_dir:
        fonts_dir = ensure_fonts()
        
    font_mapping = {
        "Work Sans": "WorkSans-Bold.ttf",
        "Montserrat": "Montserrat-ExtraBold.ttf",
        "Oswald": "Oswald-Bold.ttf",
        "Anton": "Anton-Regular.ttf",
        "Lato": "Lato-Bold.ttf",
        "Impact": "Anton-Regular.ttf"
    }
    
    target_filename = font_mapping.get(font_name, "WorkSans-Bold.ttf")
    font_path = os.path.join(fonts_dir, target_filename)
    if os.path.exists(font_path) and os.path.getsize(font_path) > 0:
        return font_path
    
    # Fallback to any existing font in fonts_dir
    for fb in ["WorkSans-Bold.ttf", "Anton-Regular.ttf", "Lato-Bold.ttf", "Montserrat-ExtraBold.ttf"]:
        p = os.path.join(fonts_dir, fb)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
            
    return font_path

def generate_cta_button_image(text: str, bg_color_hex: str, text_color_hex: str, font_name: str, resolution: str, output_path: str) -> str:
    from PIL import Image, ImageDraw, ImageFont
    
    is_1080 = (resolution == "1080p")
    font_size = 54 if is_1080 else 36
    padding_x = 70 if is_1080 else 46
    padding_y = 26 if is_1080 else 18
    radius = 35 if is_1080 else 24
        
    fonts_dir = ensure_fonts()
    font_path = get_font_file_path(font_name, fonts_dir)
        
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        try:
            fb = get_font_file_path("Work Sans", fonts_dir)
            font = ImageFont.truetype(fb, font_size)
        except:
            font = ImageFont.load_default()
        
    try:
        left, top, right, bottom = font.getbbox(text)
        text_width = right - left
        text_height = bottom - top
    except:
        text_width = len(text) * int(font_size * 0.6)
        text_height = font_size
        
    width = text_width + (padding_x * 2)
    height = text_height + (padding_y * 2)
    
    oversample = 3
    ow = width * oversample
    oh = height * oversample
    oradius = radius * oversample
    try:
        ofont = ImageFont.truetype(font_path, font_size * oversample)
    except:
        ofont = font
        
    image = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    bg_clean = (bg_color_hex or "#14AEEA").lstrip('#')
    txt_clean = (text_color_hex or "#FFFFFF").lstrip('#')
    bg_rgb = (int(bg_clean[0:2], 16), int(bg_clean[2:4], 16), int(bg_clean[4:6], 16)) if len(bg_clean) == 6 else (20, 174, 234)
    txt_rgb = (int(txt_clean[0:2], 16), int(txt_clean[2:4], 16), int(txt_clean[4:6], 16)) if len(txt_clean) == 6 else (255, 255, 255)
    
    draw.rounded_rectangle([(0, 0), (ow, oh)], radius=oradius, fill=(bg_rgb[0], bg_rgb[1], bg_rgb[2], 245), outline=(255, 255, 255, 120), width=int(2 * oversample))
    
    try:
        draw.text((ow / 2, oh / 2), text, fill=(txt_rgb[0], txt_rgb[1], txt_rgb[2], 255), font=ofont, anchor="mm")
    except:
        draw.text((padding_x * oversample, padding_y * oversample), text, fill=(txt_rgb[0], txt_rgb[1], txt_rgb[2], 255), font=ofont)
        
    final_img = image.resize((width, height), Image.Resampling.LANCZOS)
    final_img.save(output_path, "PNG")
    return output_path

def generate_watermark_badge_image(text: str, border_color_hex: str, font_name: str, resolution: str, output_path: str) -> str:
    from PIL import Image, ImageDraw, ImageFont
    
    is_1080 = (resolution == "1080p")
    font_size = 20 if is_1080 else 14
    pad_x = 24 if is_1080 else 16
    pad_y = 8 if is_1080 else 5
    border_w = 2 if is_1080 else 1.5
    
    fonts_dir = ensure_fonts()
    font_path = get_font_file_path(font_name, fonts_dir)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()
        
    text_clean = text.strip().upper()
    try:
        left, top, right, bottom = font.getbbox(text_clean)
        t_w = right - left
        t_h = bottom - top
    except:
        t_w = len(text_clean) * int(font_size * 0.6)
        t_h = font_size
        
    w = t_w + (pad_x * 2)
    h = t_h + (pad_y * 2)
    radius = h // 2
    
    oversample = 3
    ow = w * oversample
    oh = h * oversample
    oradius = radius * oversample
    oborder_w = int(border_w * oversample)
    
    try:
        ofont = ImageFont.truetype(font_path, font_size * oversample)
    except:
        ofont = font
        
    img = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background: #064A63 with 92% opacity
    bg_fill = (6, 74, 99, 235)
    
    bc = (border_color_hex or "#14AEEA").lstrip('#')
    if len(bc) == 6:
        border_rgba = (int(bc[0:2], 16), int(bc[2:4], 16), int(bc[4:6], 16), 180)
    else:
        border_rgba = (20, 174, 234, 180)
        
    draw.rounded_rectangle([(0, 0), (ow, oh)], radius=oradius, fill=bg_fill, outline=border_rgba, width=oborder_w)
    
    # Gold text: #D4AF37
    text_color = (212, 175, 55, 255)
    try:
        draw.text((ow / 2, oh / 2), text_clean, fill=text_color, font=ofont, anchor="mm")
    except:
        draw.text((pad_x * oversample, pad_y * oversample), text_clean, fill=text_color, font=ofont)
        
    final_img = img.resize((w, h), Image.Resampling.LANCZOS)
    final_img.save(output_path, "PNG")
    return output_path

def generate_title_banner_image(title_text: str, box_color_hex: str, text_color_hex: str, primary_color_hex: str, title_style: str, font_size_setting: str, font_name: str, resolution: str, output_path: str) -> str:
    from PIL import Image, ImageDraw, ImageFont
    
    is_1080 = (resolution == "1080p")
    
    if is_1080:
        base_size = 54 if font_size_setting == "large" else (64 if font_size_setting == "xlarge" else 44)
        pad_x = 32
        pad_y = 16
        radius = 20
        max_chars = 20
        line_spacing = 8
    else: # 720p
        base_size = 36 if font_size_setting == "large" else (44 if font_size_setting == "xlarge" else 28)
        pad_x = 22
        pad_y = 11
        radius = 14
        max_chars = 20
        line_spacing = 6
        
    fonts_dir = ensure_fonts()
    font_path = get_font_file_path(font_name, fonts_dir)
    
    wrapped_lines = wrap_text_smart(title_text.upper(), max_chars_per_line=max_chars).split("\n")
    if not wrapped_lines:
        wrapped_lines = [title_text.upper()]
        
    oversample = 3
    ofont_size = base_size * oversample
    try:
        ofont = ImageFont.truetype(font_path, ofont_size)
    except:
        try:
            fb = get_font_file_path("Work Sans", fonts_dir)
            ofont = ImageFont.truetype(fb, ofont_size)
        except:
            ofont = ImageFont.load_default()
            
    line_metrics = []
    max_line_w = 0
    total_text_h = 0
    for line in wrapped_lines:
        try:
            l, t, r, b = ofont.getbbox(line)
            lw = r - l
            lh = b - t
        except:
            lw = len(line) * int(ofont_size * 0.6)
            lh = ofont_size
        line_metrics.append((line, lw, lh))
        max_line_w = max(max_line_w, lw)
        total_text_h += lh
    total_text_h += (len(wrapped_lines) - 1) * (line_spacing * oversample)
    
    ow = max_line_w + (pad_x * 2 * oversample)
    oh = total_text_h + (pad_y * 2 * oversample)
    oradius = radius * oversample
    
    img = Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    box_hex = (box_color_hex or "#064A63").lstrip('#')
    txt_hex = (text_color_hex or "#FFFFFF").lstrip('#')
    pri_hex = (primary_color_hex or "#14AEEA").lstrip('#')
    
    b_rgb = (int(box_hex[0:2], 16), int(box_hex[2:4], 16), int(box_hex[4:6], 16)) if len(box_hex) == 6 else (6, 74, 99)
    t_rgb = (int(txt_hex[0:2], 16), int(txt_hex[2:4], 16), int(txt_hex[4:6], 16)) if len(txt_hex) == 6 else (255, 255, 255)
    p_rgb = (int(pri_hex[0:2], 16), int(pri_hex[2:4], 16), int(pri_hex[4:6], 16)) if len(pri_hex) == 6 else (20, 174, 234)
    
    if title_style == "box":
        draw.rounded_rectangle([(0, 0), (ow, oh)], radius=oradius, fill=(b_rgb[0], b_rgb[1], b_rgb[2], 240), outline=(p_rgb[0], p_rgb[1], p_rgb[2], 160), width=int(2 * oversample))
    elif title_style == "outline":
        draw.rounded_rectangle([(0, 0), (ow, oh)], radius=oradius, fill=(0, 0, 0, 0), outline=(p_rgb[0], p_rgb[1], p_rgb[2], 255), width=int(3 * oversample))
        
    cur_y = pad_y * oversample
    for line, lw, lh in line_metrics:
        cur_x = (ow - lw) / 2.0
        # Text drop shadow
        draw.text((cur_x + 2 * oversample, cur_y + 2 * oversample), line, fill=(0, 0, 0, 180), font=ofont)
        draw.text((cur_x, cur_y), line, fill=(t_rgb[0], t_rgb[1], t_rgb[2], 255), font=ofont)
        cur_y += lh + (line_spacing * oversample)
        
    final_w = ow // oversample
    final_h = oh // oversample
    final_img = img.resize((final_w, final_h), Image.Resampling.LANCZOS)
    final_img.save(output_path, "PNG")
    return output_path

def hex_to_ass_color(hex_color: str, alpha_hex: str = "00") -> str:
    hex_color = (hex_color or "#FFFFFF").lstrip('#')
    if len(hex_color) == 6:
        r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
        return f"&H{alpha_hex}{b}{g}{r}"
    return f"&H{alpha_hex}FFFFFF"

def wrap_text_smart(text: str, max_chars_per_line: int = 18) -> str:
    if not text:
        return ""
    words = text.strip().split()
    if not words:
        return ""
    lines = []
    current_line = []
    current_length = 0
    for w in words:
        if current_length + len(w) + (1 if current_line else 0) > max_chars_per_line:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [w]
                current_length = len(w)
            else:
                lines.append(w)
                current_line = []
                current_length = 0
        else:
            current_line.append(w)
            current_length += len(w) + (1 if len(current_line) > 1 else 0)
    if current_line:
        lines.append(" ".join(current_line))
    return "\n".join(lines)

def build_ffmpeg_command_args(video_path: str, escaped_srt_path: str, config: dict, output_path: str, start_time: str = None, duration: str = None) -> list:
    use_master_ci = config.get("use_master_ci", config.get("useMasterCi", True))
    
    show_title = config.get("showTitle", config.get("show_title", True))
    show_logo = config.get("showLogo", config.get("show_logo", True))
    show_subtitles = config.get("showSubtitles", config.get("show_subtitles", True))
    show_cta = config.get("showCTA", config.get("show_cta", True))
    
    fonts_dir = ensure_fonts()
    escaped_fonts_dir = fonts_dir.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")

    primary_color = config.get("primaryColor", "#14AEEA")
    box_color = config.get("boxColor", config.get("titleBgColor", "#064A63"))
    text_color = config.get("textColor", "#FFFFFF")
    
    logo_path = config.get("logoPath", None)
    if not logo_path or not os.path.exists(logo_path):
        mimaros_logo_candidate = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "logo_mimaros.png")
        default_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logo.png")
        if os.path.exists(mimaros_logo_candidate):
            logo_path = mimaros_logo_candidate
        elif os.path.exists(default_logo):
            logo_path = default_logo
            
    logo_pos = str(config.get("logoPosition", "top-left")).lower().replace("-", "_")
    font_name = config.get("fontName", "Work Sans")
    
    hook_header = config.get("hookHeader", config.get("hook_header", "")).strip()
    has_title = bool(hook_header and show_title)
    
    resolution = config.get("resolution", "720p")
    is_1080 = (resolution == "1080p")
    
    if is_1080:
        vf_scale = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
        border_thickness = 10
        logo_width = 82
        margin_x = 36
        margin_y = 24
    else:
        vf_scale = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280"
        border_thickness = 6
        logo_width = 54
        margin_x = 24
        margin_y = 16

    # Base stream with scaling & CI border
    vf_filter = f"[0:v]{vf_scale}"
    if use_master_ci:
        vf_filter += f",drawbox=x=0:y=0:w=iw:h=ih:color={primary_color}:thickness={border_thickness}"
        
    # Subtitles rendered via ASS
    if show_subtitles:
        vf_filter += f",subtitles='{escaped_srt_path}':fontsdir='{escaped_fonts_dir}'"
        
    vf_filter += "[v_base]"
    filter_complex = vf_filter
    inputs = [video_path]
    current_v = "[v_base]"
    
    base_dir = os.path.dirname(os.path.abspath(output_path))
    
    # 1. Overlay Watermark / Domain Badge (Rounded Pill)
    watermark_text = config.get("watermark_text", "mimaros.eu").strip()
    if watermark_text and use_master_ci:
        watermark_img_path = os.path.join(base_dir, f"wm_{os.path.basename(output_path)}.png")
        try:
            generate_watermark_badge_image(watermark_text, primary_color, font_name, resolution, watermark_img_path)
            inputs.append(watermark_img_path)
            wm_idx = len(inputs) - 1
            wm_y = 24 if is_1080 else 16
            filter_complex += f";[{wm_idx}:v]scale=-1:-1[wm_img];{current_v}[wm_img]overlay=x=(W-w)/2:y={wm_y}[v_wm]"
            current_v = "[v_wm]"
        except Exception as e:
            print(f"Error generating watermark badge: {e}")

    # 2. Overlay Logo
    if logo_path and os.path.exists(logo_path) and show_logo:
        inputs.append(logo_path)
        logo_input_index = len(inputs) - 1
        
        if "bottom" in logo_pos:
            y_pos = f"H-h-{margin_y}"
        else:
            y_pos = f"{margin_y}"
            
        if "right" in logo_pos:
            x_pos = f"W-w-{margin_x}"
        elif "center" in logo_pos or "middle" in logo_pos:
            x_pos = f"(W-w)/2"
        else:
            x_pos = f"{margin_x}"
            
        filter_complex += f";[{logo_input_index}:v]scale={logo_width}:-2[logo];{current_v}[logo]overlay=x={x_pos}:y={y_pos}[v_logo]"
        current_v = "[v_logo]"
        
    # 3. Overlay Title Banner (Rounded Box / Outline / Clean)
    if has_title:
        title_style = str(config.get("titleStyle", "box")).lower()
        title_font_size = str(config.get("titleFontSize", "normal")).lower()
        title_pos = str(config.get("titlePosition", "top")).lower()
        
        title_img_path = os.path.join(base_dir, f"title_{os.path.basename(output_path)}.png")
        try:
            generate_title_banner_image(hook_header, box_color, text_color, primary_color, title_style, title_font_size, font_name, resolution, title_img_path)
            inputs.append(title_img_path)
            title_idx = len(inputs) - 1
            
            if "center" in title_pos or "middle" in title_pos:
                t_y_pos = "(H-h)*0.33"
            elif "bottom" in title_pos:
                t_y_pos = "H-h-360" if is_1080 else "H-h-240"
            else: # top (positioned cleanly below the watermark badge)
                t_y_pos = "96" if is_1080 else "64"
                
            filter_complex += f";[{title_idx}:v]scale=-1:-1[title_img];{current_v}[title_img]overlay=x=(W-w)/2:y={t_y_pos}[v_title]"
            current_v = "[v_title]"
        except Exception as e:
            print(f"Error generating title banner: {e}")

    # 4. Overlay CTA Button
    cta = config.get("cta", "none")
    cta_text = ""
    if cta == "subscribe":
        cta_text = "JETZT ABONNIEREN"
    elif cta == "follow":
        cta_text = "FOLGEN FÜR MEHR"
    elif cta == "more":
        cta_text = "MEHR VIDEOS"
        
    if cta_text and show_cta:
        cta_img_path = os.path.join(base_dir, f"cta_{os.path.basename(output_path)}.png")
        try:
            generate_cta_button_image(cta_text, primary_color, "#FFFFFF", font_name, resolution, cta_img_path)
            inputs.append(cta_img_path)
            cta_input_index = len(inputs) - 1
            
            dur_val = float(duration) if duration else 0.0
            intervals = []
            if dur_val > 0.0:
                half_time = dur_val / 2.0
                intervals.append((half_time, min(half_time + 4.0, dur_val)))
                if dur_val > 45.0:
                    t = 30.0
                    while t < dur_val:
                        if not (t >= half_time - 4.0 and t <= half_time + 4.0):
                            intervals.append((t, min(t + 4.0, dur_val)))
                        t += 30.0
            else:
                intervals.append((0.5, 3.0))
            
            if intervals:
                enable_expr = "+".join([f"between(t,{start},{end})" for start, end in intervals])
                fade_chain = f"[{cta_input_index}:v]loop=loop=-1:size=1:start=0,setpts=PTS-STARTPTS"
                for start, end in intervals:
                    fade_chain += f",fade=t=in:st={start}:d=0.5:alpha=1,fade=t=out:st={end-0.5}:d=0.5:alpha=1"
                fade_chain += "[cta_faded]"
                
                filter_complex += f";{fade_chain};{current_v}[cta_faded]overlay=x=(W-w)/2:y=(H-h)/2:enable='{enable_expr}'[v_cta]"
                current_v = "[v_cta]"
        except Exception as e:
            print(f"Error generating CTA image button: {e}")
            
    # Voiceover Audio Overlay Handling
    voiceover_path = config.get("voiceover_path", None)
    if not voiceover_path and config.get("voiceoverUrl"):
        v_url = config.get("voiceoverUrl")
        v_name = os.path.basename(v_url)
        v_local = os.path.join(os.path.dirname(output_path), "..", "Fertige_Shorts", v_name)
        if os.path.exists(v_local):
            voiceover_path = v_local
            
    voiceover_input_index = -1
    if voiceover_path and os.path.exists(voiceover_path):
        inputs.append(voiceover_path)
        voiceover_input_index = len(inputs) - 1

    map_v = current_v
    audio_map = f"{voiceover_input_index}:a" if voiceover_input_index != -1 else "0:a?"
    
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
        "-map", audio_map,
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
    Generiert eine professionelle .ass Datei mit separaten Styles für
    Untertitel (Karaoke, Dynamic Box, Pop-Up Bouncy, Hormozi, MIMAROS Clean)
    UND Video-Titel (mit präzisen Farben, Schriftarten, Abständen und CI-Branding).
    """
    if config is None:
        config = {}
    
    # 1. Colors parsing
    highlight_color_hex = config.get("highlightColor", "#D4AF37")
    text_color_hex = config.get("textColor", "#ffffff")
    primary_color_hex = config.get("primaryColor", "#14AEEA")
    box_color_hex = config.get("boxColor", config.get("titleBgColor", "#064A63"))
    title_color_hex = config.get("titleColor", text_color_hex)
    
    highlight_color_ass = hex_to_ass_color(highlight_color_hex, "00") + "&"
    text_color_ass = hex_to_ass_color(text_color_hex, "00")
    primary_color_ass = hex_to_ass_color(primary_color_hex, "00")
    box_color_ass = hex_to_ass_color(box_color_hex, "26") # 85% opacity
    title_color_ass = hex_to_ass_color(title_color_hex, "00")
    title_box_ass = hex_to_ass_color(box_color_hex, "26")
    
    # 2. Font configuration
    font_name = config.get("fontName", "Work Sans")
    if font_name in ["Work Sans", "Montserrat", "Anton", "Oswald", "Lato"]:
        ass_font = font_name
    elif font_name:
        ass_font = font_name
    else:
        ass_font = "Work Sans"
        
    # 3. Resolution scaling
    resolution = config.get("resolution", "720p")
    is_1080 = (resolution == "1080p")
    
    # Subtitle Font Size & Position
    sub_size_setting = str(config.get("subtitleFontSize", "normal")).lower()
    if sub_size_setting == "large":
        sub_font_size = 76 if is_1080 else 50
    elif sub_size_setting in ["xlarge", "extra-large", "extra_large"]:
        sub_font_size = 88 if is_1080 else 58
    else: # normal
        sub_font_size = 64 if is_1080 else 42
        
    # Title Font Size
    title_size_setting = str(config.get("titleFontSize", "normal")).lower()
    if title_size_setting == "large":
        title_font_size = 66 if is_1080 else 44
    elif title_size_setting in ["xlarge", "extra-large", "extra_large"]:
        title_font_size = 78 if is_1080 else 52
    else: # normal
        title_font_size = 56 if is_1080 else 38
        
    # Margin settings - Safe Zone well above bottom UI (caption, audio title, action buttons)
    ass_margin_lr = 80 if is_1080 else 50
    ass_margin_v = int(config.get("subtitleMarginV", 390 if is_1080 else 260))
    
    # Title options
    show_title = config.get("showTitle", config.get("show_title", True))
    hook_header = config.get("hookHeader", config.get("hook_header", "")).strip()
    title_pos = str(config.get("titlePosition", "top")).lower()
    title_style = str(config.get("titleStyle", "box")).lower()
    show_logo = config.get("showLogo", config.get("show_logo", True))
    logo_pos = str(config.get("logoPosition", "top-left")).lower()
    
    if "center" in title_pos or "middle" in title_pos:
        title_alignment = 5
        title_margin_v = 0
    elif "bottom" in title_pos:
        title_alignment = 2
        title_margin_v = 520 if is_1080 else 350
    else: # top (default)
        title_alignment = 8
        if show_logo and "top" in logo_pos:
            title_margin_v = 140 if is_1080 else 90
        else:
            title_margin_v = 130 if is_1080 else 85
            
    # Title border style
    if title_style == "outline":
        title_border_mode = 1
        title_outline_w = 4.5 if is_1080 else 3.0
        title_shadow_w = 2.5 if is_1080 else 1.8
        title_outline_col = "&H00000000"
    elif title_style == "clean":
        title_border_mode = 1
        title_outline_w = 1.5 if is_1080 else 1.0
        title_shadow_w = 2.0 if is_1080 else 1.5
        title_outline_col = "&H00000000"
    else: # "box" / default MIMAROS Corporate Box
        title_border_mode = 3
        title_outline_w = 16 if is_1080 else 11 # Generous Box padding in pixels
        title_shadow_w = 0
        title_outline_col = primary_color_ass # Glowing border
        
    design = config.get("design", "mimaros_clean")
    show_subtitles = config.get("showSubtitles", config.get("show_subtitles", True))
    
    def format_ass_time(seconds: float) -> str:
        seconds = max(0.0, seconds)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centis = int(round((seconds % 1) * 100))
        if centis >= 100:
            secs += 1
            centis = 0
        return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

    clip_duration = max(0.1, end_time - start_time)

    try:
        with open(ass_path, 'w', encoding='utf-8') as f:
            # 1. Write ASS Header
            f.write("[Script Info]\n")
            f.write("ScriptType: v4.00+\n")
            f.write("PlayResX: 1080\n" if is_1080 else "PlayResX: 720\n")
            f.write("PlayResY: 1920\n" if is_1080 else "PlayResY: 1280\n")
            f.write("ScaledBorderAndShadow: yes\n\n")
            
            # 2. Write Styles
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            
            # Subtitle Styles mapped 1:1 to modern social media shorts
            if design == "mimaros_clean":
                f.write(f"Style: Default,{ass_font},{sub_font_size},{text_color_ass},&H000000FF,&H00000000,&HC0000000,-1,0,0,0,100,100,0,0,1,4.0,2.0,2,{ass_margin_lr},{ass_margin_lr},{ass_margin_v},1\n")
            elif design == "dynamic_box":
                f.write(f"Style: Default,{ass_font},{sub_font_size},{text_color_ass},&H000000FF,&H00000000,&HC0000000,-1,0,0,0,100,100,0,0,1,4.0,2.5,2,{ass_margin_lr},{ass_margin_lr},{ass_margin_v},1\n")
            elif design == "popup_bouncy":
                f.write(f"Style: Default,{ass_font},{sub_font_size + 14},{highlight_color_ass},&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,1,4.5,2.5,5,{ass_margin_lr},{ass_margin_lr},0,1\n")
            elif design == "hormozi":
                f.write(f"Style: Default,Anton,{sub_font_size + 16},{text_color_ass},&H000000FF,&H00000000,&HFF000000,-1,0,0,0,100,100,0,0,1,6.0,0,2,{ass_margin_lr},{ass_margin_lr},{ass_margin_v},1\n")
            else: # karaoke
                f.write(f"Style: Default,{ass_font},{sub_font_size},{text_color_ass},&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,1,4.5,2.5,2,{ass_margin_lr},{ass_margin_lr},{ass_margin_v},1\n")
                
            f.write("\n")
            
            # 3. Write Subtitle Events
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            
            if show_subtitles:
                for segment in segments:
                    if "words" in segment and segment["words"]:
                        words_in_range = []
                        for word in segment["words"]:
                            w_start = float(word["start"])
                            w_end = float(word["end"])
                            w_text = word["word"].strip()
                            if w_end > start_time and w_start < end_time and w_text:
                                words_in_range.append({"text": w_text, "start": max(start_time, w_start), "end": min(end_time, w_end)})
                                
                        if not words_in_range:
                            continue
                            
                        if design == "popup_bouncy":
                            chunk_size = 1
                        elif design == "hormozi":
                            chunk_size = 2
                        elif design == "mimaros_clean":
                            chunk_size = 4
                        else: # karaoke / dynamic_box
                            chunk_size = 3
                            
                        for chunk_idx in range(0, len(words_in_range), chunk_size):
                            chunk = words_in_range[chunk_idx : chunk_idx + chunk_size]
                            if not chunk:
                                continue
                                
                            chunk_start = max(0.0, chunk[0]["start"] - start_time)
                            chunk_end = max(chunk_start + 0.2, chunk[-1]["end"] - start_time)
                            
                            for i, active_word in enumerate(chunk):
                                if i == 0:
                                    event_start = chunk_start
                                else:
                                    event_start = max(0.0, chunk[i]["start"] - start_time)
                                    
                                if i == len(chunk) - 1:
                                    event_end = chunk_end
                                else:
                                    event_end = max(event_start + 0.1, chunk[i+1]["start"] - start_time)
                                    
                                formatted_words = []
                                for j, w in enumerate(chunk):
                                    w_text = w["text"].upper()
                                    if design == "mimaros_clean":
                                        if j == i:
                                            formatted_words.append(f"{{\\c{highlight_color_ass}}}{w_text}{{\\rDefault}}")
                                        else:
                                            formatted_words.append(w_text)
                                    elif design == "hormozi":
                                        if j == i:
                                            h_col = highlight_color_ass if highlight_color_hex != "#D4AF37" else ("&H0000FFFF&" if i % 2 == 0 else "&H0000FF00&")
                                            formatted_words.append(f"{{\\c{h_col}\\fscx112\\fscy112}}{w_text}{{\\rDefault}}")
                                        else:
                                            formatted_words.append(w_text)
                                    elif design == "popup_bouncy":
                                        formatted_words.append(f"{{\\t(0,60,\\fscx125\\fscy125)\\t(60,130,\\fscx100\\fscy100)\\c{highlight_color_ass}}}{w_text}{{\\rDefault}}")
                                    elif design == "dynamic_box":
                                        if j == i:
                                            formatted_words.append(f"{{\\c{highlight_color_ass}\\fscx108\\fscy108}}{w_text}{{\\rDefault}}")
                                        else:
                                            formatted_words.append(w_text)
                                    else: # karaoke highlight
                                        if j == i:
                                            formatted_words.append(f"{{\\c{highlight_color_ass}\\fscx112\\fscy112}}{w_text}{{\\rDefault}}")
                                        else:
                                            formatted_words.append(w_text)
                                            
                                chunk_text = " ".join(formatted_words)
                                if design == "mimaros_clean":
                                    chunk_text = f"{{\\fad(80,80)}}{chunk_text}"
                                    
                                f.write(f"Dialogue: 1,{format_ass_time(event_start)},{format_ass_time(event_end)},Default,,0,0,0,,{chunk_text}\n")
                    else:
                        # Fallback for segment-only without word timestamps
                        s_start = float(segment.get("start", 0.0))
                        s_end = float(segment.get("end", 0.0))
                        s_text = segment.get("text", "").strip().upper()
                        if s_end > start_time and s_start < end_time and s_text:
                            rel_start = max(0.0, s_start - start_time)
                            rel_end = min(clip_duration, s_end - start_time)
                            fade_tag = "{\\fad(100,100)}" if design == "mimaros_clean" else ""
                            f.write(f"Dialogue: 1,{format_ass_time(rel_start)},{format_ass_time(rel_end)},Default,,0,0,0,,{fade_tag}{s_text}\n")
    except Exception as e:
        print(f"Failed to generate ASS file: {e}")
        raise e

def detect_speech_intervals(segments: list, start_time: float, end_time: float, min_silence_pad: float = 0.15) -> list:
    """
    Ermittelt anhand der Transkriptions-Segmente und Wörter alle aktiven Sprachintervalle
    und schneidet Pausen > 0.4 Sekunden heraus.
    """
    intervals = []
    current_start = None
    current_end = None
    
    # Sammle alle Wörter/Segmente im angegebenen Zeitbereich
    active_blocks = []
    for seg in segments:
        words = seg.get("words", [])
        if words:
            for w in words:
                ws, we = float(w["start"]), float(w["end"])
                if ws >= start_time and we <= end_time:
                    active_blocks.append((ws, we))
        else:
            ss, se = float(seg["start"]), float(seg["end"])
            if ss >= start_time and se <= end_time:
                active_blocks.append((ss, se))
                
    if not active_blocks:
        return [(start_time, end_time)]
        
    active_blocks.sort(key=lambda x: x[0])
    
    # Verschmelze Blöcke mit weniger als 0.4 Sekunden Abstand
    merged = []
    cur_s, cur_e = active_blocks[0]
    for next_s, next_e in active_blocks[1:]:
        if next_s - cur_e <= 0.4:
            cur_e = max(cur_e, next_e)
        else:
            merged.append((max(start_time, cur_s - min_silence_pad), min(end_time, cur_e + min_silence_pad)))
            cur_s, cur_e = next_s, next_e
    merged.append((max(start_time, cur_s - min_silence_pad), min(end_time, cur_e + min_silence_pad)))
    
    return merged

def process_clip(video_path: str, transcript_data: dict, start_time: float, end_time: float, output_path: str, resolution: str = "720p", subtitle_config: dict = None):
    if subtitle_config is None:
        subtitle_config = {}
    subtitle_config["resolution"] = resolution
    
    base_dir = os.path.dirname(os.path.abspath(output_path))
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
        for ext_p in [ass_path, os.path.join(base_dir, f"cta_{os.path.basename(output_path)}.png"), os.path.join(base_dir, f"wm_{os.path.basename(output_path)}.png"), os.path.join(base_dir, f"title_{os.path.basename(output_path)}.png")]:
            if os.path.exists(ext_p):
                try: os.remove(ext_p)
                except: pass

def generate_preview(video_path: str, output_path: str, config: dict):
    base_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(base_dir, exist_ok=True)
    dummy_ass_path = os.path.join(base_dir, f"dummy_{os.path.basename(output_path)}.ass")
    
    # Mock segment with word timestamps synchronized with hookHeader/preview_text
    preview_words_str = config.get("hookHeader") or config.get("preview_text") or "DER GEHEIME TRICK FÜR VIRALE CLIPS"
    raw_words = preview_words_str.strip().split()
    if not raw_words:
        raw_words = ["DER", "GEHEIME", "TRICK", "FÜR", "VIRALE", "CLIPS"]
        
    dur_per_word = 3.0 / max(1, len(raw_words))
    mock_words = []
    for i, w in enumerate(raw_words):
        mock_words.append({
            "word": w.upper(),
            "start": round(i * dur_per_word, 2),
            "end": round((i + 1) * dur_per_word, 2)
        })
        
    mock_segments = [
        {
            "start": 0.0,
            "end": 3.0,
            "text": " ".join([w["word"] for w in mock_words]),
            "words": mock_words
        }
    ]
    
    config["resolution"] = "720p"
    generate_ass(mock_segments, 0.0, 3.0, dummy_ass_path, config)
    escaped_ass_path = dummy_ass_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
    
    command = build_ffmpeg_command_args(video_path, escaped_ass_path, config, output_path, start_time="0", duration="3")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            error_msg = result.stderr[-1000:] if result.stderr and len(result.stderr) > 1000 else result.stderr
            raise RuntimeError(f"FFmpeg Error: {error_msg}")
    finally:
        for ext_p in [dummy_ass_path, os.path.join(base_dir, f"cta_{os.path.basename(output_path)}.png"), os.path.join(base_dir, f"wm_{os.path.basename(output_path)}.png"), os.path.join(base_dir, f"title_{os.path.basename(output_path)}.png")]:
            if os.path.exists(ext_p):
                try: os.remove(ext_p)
                except: pass

def normalize_clip(input_path: str, output_path: str, resolution: str = "1080p"):
    """
    Normiert einen Clip strikt auf 9:16 Center-Crop, 30fps und 48000Hz Stereo Audio.
    Dies ist essenziell, damit FFmpeg xfade reibungslos funktioniert.
    """
    if resolution == "1080p":
        vf_scale = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30"
    else:
        vf_scale = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30"
        
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
        for ext_p in [ass_path, os.path.join(base_dir, f"cta_{os.path.basename(output_path)}.png"), os.path.join(base_dir, f"wm_{os.path.basename(output_path)}.png"), os.path.join(base_dir, f"title_{os.path.basename(output_path)}.png")]:
            if os.path.exists(ext_p):
                try: os.remove(ext_p)
                except: pass
