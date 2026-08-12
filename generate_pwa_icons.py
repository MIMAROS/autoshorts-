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

def generate_svg_logo():
    return '''<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="mimarosGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#56CCF2" />
      <stop offset="100%" stop-color="#F2994A" />
    </linearGradient>
  </defs>
  <circle cx="50" cy="50" r="44" fill="#0B111A" stroke="url(#mimarosGrad)" stroke-width="4"/>
  <polygon points="42,34 42,66 68,50" fill="url(#mimarosGrad)"/>
</svg>'''

dirs = [
    r"C:\Users\Miguel\Documents\AutoShorts\frontend\public",
    r"C:\Users\Miguel\Projects\Sociel Meidia Auto Posting App\frontend\public"
]

files_to_remove = [
    "apple-touch-icon-precomposed.png",
    "apple-touch-icon.png",
    "favicon-16x16.png",
    "favicon-32x32.png",
    "favicon.ico",
    "favicon.svg",
    "icon-192.png",
    "icon-512.png",
    "icon.png",
    "logo.png",
    "logo.svg"
]

for base_path in dirs:
    os.makedirs(base_path, exist_ok=True)
    # Bereinigung alter Dateien
    for f in files_to_remove:
        p = os.path.join(base_path, f)
        if os.path.exists(p):
            try:
                os.remove(p)
                print(f"Gelöscht: {p}")
            except Exception as e:
                print(f"Fehler beim Löschen von {p}: {e}")

    # Neu-Erzeugung aller Icon & Logo Dateien mit neuem Kreis-Play Design
    icon_192 = create_mimaros_minimalist_icon(192)
    icon_192.save(os.path.join(base_path, "icon-192.png"), "PNG")

    icon_512 = create_mimaros_minimalist_icon(512)
    icon_512.save(os.path.join(base_path, "icon-512.png"), "PNG")
    icon_512.save(os.path.join(base_path, "icon.png"), "PNG")
    icon_512.save(os.path.join(base_path, "logo.png"), "PNG")

    icon_180 = create_mimaros_minimalist_icon(180)
    icon_180.save(os.path.join(base_path, "apple-touch-icon.png"), "PNG")
    icon_180.save(os.path.join(base_path, "apple-touch-icon-precomposed.png"), "PNG")

    icon_32 = create_mimaros_minimalist_icon(32)
    icon_32.save(os.path.join(base_path, "favicon.ico"), "ICO", sizes=[(32, 32)])
    icon_32.save(os.path.join(base_path, "favicon-32x32.png"), "PNG")

    icon_16 = create_mimaros_minimalist_icon(16)
    icon_16.save(os.path.join(base_path, "favicon-16x16.png"), "PNG")

    svg_content = generate_svg_logo()
    with open(os.path.join(base_path, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)
    with open(os.path.join(base_path, "logo.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)

print("Public-Ordner erfolgreich bereinigt und alle Icons/Logos neu erstellt!")
