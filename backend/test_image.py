import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("--- Teste alternative Bildgenerierungs-Methoden ---")

models_to_test = [
    'imagen-4.0-fast-generate-001',
    'imagen-4.0-ultra-generate-001',
    'gemini-3.1-flash-lite-image',
    'gemini-3-pro-image'
]

for model_name in models_to_test:
    print(f"\nTeste generate_images mit {model_name}:")
    try:
        response = client.models.generate_images(
            model=model_name,
            prompt='A sleek dark blue background with gold accents, 9:16 aspect ratio',
            config=dict(
                number_of_images=1,
                aspect_ratio="9:16"
            )
        )
        print("-> Erfolg!")
        print(f"Bilder erhalten: {len(response.generated_images)}")
    except Exception as e:
        print(f"-> Fehler: {e}")

for model_name in models_to_test:
    print(f"\nTeste generate_content mit {model_name}:")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents='A sleek dark blue background with gold accents, 9:16 aspect ratio'
        )
        print("-> Erfolg!")
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                print("-> InlineData gefunden! Bild-Bytes sind vorhanden.")
    except Exception as e:
        print(f"-> Fehler: {e}")

