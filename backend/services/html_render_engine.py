import os
import asyncio
from playwright.async_api import async_playwright

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Mimaros Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Work+Sans:wght@700;800&family=Poppins:wght@600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-bg: #0B111A;
            --secondary-bg: #101A24;
            --accent-gold: #C89B31;
            --accent-cyan: #14AEEA;
            --text-color: #EEF3F8;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            background-color: var(--primary-bg);
            background-image: url('{background_image_url}');
            background-size: cover;
            background-position: center;
            color: var(--text-color);
            font-family: 'Lato', sans-serif;
            width: 1080px;
            height: 1920px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 80px;
            position: relative;
        }}
        
        /* Mimaros CI Gold-Rahmen */
        .border-outline {{
            position: absolute;
            top: 30px;
            left: 30px;
            right: 30px;
            bottom: 30px;
            border: 4px solid var(--accent-gold);
            pointer-events: none;
            z-index: 10;
        }}
        .border-inner {{
            position: absolute;
            top: 45px;
            left: 45px;
            right: 45px;
            bottom: 45px;
            border: 2px solid var(--secondary-bg);
            pointer-events: none;
            z-index: 10;
        }}
        
        header {{
            margin-top: 60px;
            display: flex;
            flex-direction: column;
            align-items: center;
            z-index: 2;
        }}
        
        .eyebrow {{
            font-family: 'Poppins', sans-serif;
            font-size: 26px;
            color: var(--accent-cyan);
            text-transform: uppercase;
            letter-spacing: 5px;
            margin-bottom: 20px;
        }}
        
        h1 {{
            font-family: 'Work Sans', sans-serif;
            font-size: 60px;
            font-weight: 800;
            text-align: center;
            line-height: 1.25;
            color: #FFFFFF;
            max-width: 900px;
            text-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }}
        
        /* Bento Grid Layout */
        .bento-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            grid-template-rows: repeat(3, 1fr);
            gap: 35px;
            width: 100%;
            height: 1150px;
            margin: 40px 0;
            z-index: 2;
        }}
        
        .bento-card {{
            background-color: rgba(16, 26, 36, 0.75);
            border: 2px solid rgba(20, 174, 234, 0.2);
            border-radius: 28px;
            padding: 45px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            overflow: hidden;
            /* Glassmorphism */
            backdrop-filter: blur(15px);
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        }}
        
        .bento-card.highlight-cyan {{
            border-color: var(--accent-cyan);
            box-shadow: 0 0 25px rgba(20, 174, 234, 0.25);
        }}
        
        .bento-card.highlight-gold {{
            border-color: var(--accent-gold);
            box-shadow: 0 0 25px rgba(200, 155, 49, 0.25);
        }}
        
        .card-large {{
            grid-column: span 2;
            grid-row: span 1;
        }}
        
        .card-title {{
            font-family: 'Work Sans', sans-serif;
            font-size: 34px;
            color: var(--accent-gold);
            margin-bottom: 20px;
            font-weight: 700;
            letter-spacing: 1px;
        }}
        
        .card-body {{
            font-size: 32px;
            line-height: 1.45;
            color: var(--text-color);
        }}
        
        .metric {{
            font-family: 'Poppins', sans-serif;
            font-size: 80px;
            font-weight: 600;
            color: #FFFFFF;
            margin-bottom: 12px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        
        footer {{
            margin-bottom: 60px;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 2;
        }}
        
        .web-link {{
            font-family: 'Poppins', sans-serif;
            font-size: 30px;
            color: var(--accent-cyan);
            text-decoration: none;
            letter-spacing: 3px;
            text-shadow: 0 2px 8px rgba(0,0,0,0.4);
        }}
    </style>
</head>
<body>
    <div class="border-outline"></div>
    <div class="border-inner"></div>
    
    <header>
        <div class="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
    </header>
    
    <div class="bento-grid">
        <div class="bento-card card-large highlight-cyan">
            <div class="card-title" style="color: var(--accent-cyan)">Fokus des Tages</div>
            <div class="card-body" style="font-size: 36px;">{card_large_body}</div>
        </div>
        
        <div class="bento-card">
            <div class="metric">{metric}</div>
            <div class="card-body" style="font-size: 28px;">{card_left_body}</div>
        </div>
        
        <div class="bento-card highlight-gold">
            <div class="card-title">Mimaros Tipp</div>
            <div class="card-body" style="font-size: 28px;">{card_right_body}</div>
        </div>
        
        <div class="bento-card card-large">
            <div class="card-title" style="font-size: 30px;">Umsetzung</div>
            <div class="card-body" style="font-size: 30px;">{card_bottom_body}</div>
        </div>
    </div>
    
    <footer>
        <span class="web-link">www.mimaros.eu</span>
    </footer>
</body>
</html>
"""

async def render_html_slide(title: str, text_content: str, background_image_path: str, output_path: str):
    # Zerlege den Text in logische Absätze
    paragraphs = [p.strip() for p in text_content.split('.') if p.strip()]
    
    card_large = paragraphs[0] if len(paragraphs) > 0 else "High-End Design für Präsentationen."
    card_left = paragraphs[1] if len(paragraphs) > 1 else "Kognitive Last wird um 40% reduziert."
    card_right = paragraphs[2] if len(paragraphs) > 2 else "Nutze Bento-Raster für bessere Lesbarkeit."
    card_bottom = paragraphs[3] if len(paragraphs) > 3 else "Fokus auf die wesentlichen Kernbotschaften legen."
    
    # Metrik extrahieren falls vorhanden
    metric_text = "40%"
    if len(paragraphs) > 1:
        for word in card_left.split():
            if "%" in word or any(char.isdigit() for char in word):
                metric_text = word
                break
                
    # Hintergrundpfad als File-URL formatieren
    bg_url = "file:///" + background_image_path.replace('\\', '/')
    
    html_content = HTML_TEMPLATE.format(
        background_image_url=bg_url,
        eyebrow="MIMAROS AUTO-POST",
        title=title,
        card_large_body=card_large,
        metric=metric_text,
        card_left_body=card_left,
        card_right_body=card_right,
        card_bottom_body=card_bottom
    )
    
    temp_html_path = output_path + ".temp.html"
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1080, "height": 1920})
        await page.goto("file:///" + temp_html_path.replace('\\', '/'))
        
        # 1 Sekunde warten, damit Google Fonts geladen werden
        await page.wait_for_timeout(1000)
        
        await page.screenshot(path=output_path, type="png")
        await browser.close()
        
    try:
        os.remove(temp_html_path)
    except:
        pass
        
    print(f"HTML Slide erfolgreich gerendert: {output_path}")
    return output_path
