import asyncio
import sys
import os
from services.auto_generator import run_end_to_end_pipeline

async def main():
    # Definiere den Ausgabepfad im Ordner Fertige_Shorts
    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Fertige_Shorts")
    os.makedirs(export_dir, exist_ok=True)
    output_path = os.path.join(export_dir, "Bento_Grid_Automation.mp4")
    
    print(f"Starte vollautomatische Videoproduktion für Thema: Bento-Grid...")
    try:
        await run_end_to_end_pipeline(
            "Bento-Grid: Der C-Level-Design-Standard",
            output_path
        )
        print("Fertig! Das Video wurde erfolgreich erstellt.")
    except Exception as e:
        print(f"Fehler bei der Videoproduktion: {e}")

if __name__ == "__main__":
    asyncio.run(main())
