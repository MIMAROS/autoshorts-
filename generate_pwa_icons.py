import os
from PIL import Image, ImageDraw

def create_mimaros_minimalist_icon(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    margin = int(size * 0.05)
    radius = int(size * 0.22)
    bg_color = (11, 17, 26, 255) # Obsidian Dark #0B111A
    
    # Draw rounded rectangle background
    draw.rounded_rectangle([margin, margin, size - margin, size - margin], radius=radius, fill=bg_color)
    
    # Circle + Play Button geometry
    center = size / 2.0
    r = size * 0.38
    stroke_w = max(2, int(size * 0.04))
    
    bbox = [center - r, center - r, center + r, center + r]
    # Draw circle outline in cyan/orange blend
    draw.ellipse(bbox, outline=(86, 204, 242, 255), width=stroke_w)
    
    # Play polygon: points 42,34 -> 42,66 -> 68,50 (scaled to size)
    poly = [
        (size * 0.42, size * 0.34),
        (size * 0.42, size * 0.66),
        (size * 0.68, size * 0.50)
    ]
    draw.polygon(poly, fill=(242, 153, 74, 255))
    
    return img

for base_path in [
    r"C:\Users\Miguel\Documents\AutoShorts\frontend\public",
    r"C:\Users\Miguel\Projects\Sociel Meidia Auto Posting App\frontend\public"
]:
    os.makedirs(base_path, exist_ok=True)
    icon_192 = create_mimaros_minimalist_icon(192)
    icon_192.save(os.path.join(base_path, "icon-192.png"), "PNG")

    icon_512 = create_mimaros_minimalist_icon(512)
    icon_512.save(os.path.join(base_path, "icon-512.png"), "PNG")
    icon_512.save(os.path.join(base_path, "icon.png"), "PNG")

    icon_180 = create_mimaros_minimalist_icon(180)
    icon_180.save(os.path.join(base_path, "apple-touch-icon.png"), "PNG")
    icon_180.save(os.path.join(base_path, "apple-touch-icon-precomposed.png"), "PNG")

    icon_32 = create_mimaros_minimalist_icon(32)
    icon_32.save(os.path.join(base_path, "favicon.ico"), "ICO", sizes=[(32, 32)])
    icon_32.save(os.path.join(base_path, "favicon-32x32.png"), "PNG")

    icon_16 = create_mimaros_minimalist_icon(16)
    icon_16.save(os.path.join(base_path, "favicon-16x16.png"), "PNG")

print("All Minimalist PWA & Apple Touch Icons successfully generated for both directories!")
