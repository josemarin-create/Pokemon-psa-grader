from pathlib import Path
from io import BytesIO
import random

import pandas as pd
import requests
from PIL import Image, ImageEnhance, ImageDraw, ImageFilter


# Rutas principales del proyecto.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = PROJECT_ROOT / "data" / "processed" / "pokemon_tcg_sample.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "synthetic"

# Clases que queremos generar para el modelo baseline.
CONDITION_LABELS = ["mint", "played", "damaged"]


def load_card_sample(limit: int = 20) -> pd.DataFrame:
    # Cargamos la muestra generada en el EDA.
    df = pd.read_csv(INPUT_CSV)

    # Nos quedamos solo con cartas que tienen imagen grande disponible.
    df = df.dropna(subset=["image_large"])

    # Limitamos el numero de cartas para generar un dataset pequeño y rapido.
    return df.head(limit)


def download_image(image_url: str) -> Image.Image:
    # Descargamos una imagen desde la URL oficial.
    response = requests.get(image_url, timeout=15)
    response.raise_for_status()

    # Convertimos los bytes descargados en una imagen RGB.
    image = Image.open(BytesIO(response.content)).convert("RGB")
    return image


def resize_image(image: Image.Image, size: tuple[int, int] = (224, 312)) -> Image.Image:
    # Redimensionamos todas las imagenes al mismo tamaño.
    return image.resize(size)


def create_mint_image(image: Image.Image) -> Image.Image:
    # Mint representa una carta casi perfecta, con cambios visuales minimos.
    brightness = ImageEnhance.Brightness(image).enhance(random.uniform(0.95, 1.05))
    contrast = ImageEnhance.Contrast(brightness).enhance(random.uniform(0.95, 1.05))
    return contrast


def add_scratches(image: Image.Image, amount: int, intensity: int) -> Image.Image:
    # Dibujamos lineas claras para simular scratches en la superficie.
    damaged = image.copy()
    draw = ImageDraw.Draw(damaged)

    width, height = damaged.size

    for _ in range(amount):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = min(width, x1 + random.randint(10, 80))
        y2 = min(height, y1 + random.randint(-20, 20))

        color = (intensity, intensity, intensity)
        draw.line((x1, y1, x2, y2), fill=color, width=random.randint(1, 2))

    return damaged


def add_border_wear(image: Image.Image, amount: int) -> Image.Image:
    # Añadimos puntos claros cerca de los bordes para simular desgaste.
    worn = image.copy()
    draw = ImageDraw.Draw(worn)

    width, height = worn.size

    for _ in range(amount):
        edge = random.choice(["top", "bottom", "left", "right"])

        if edge == "top":
            x = random.randint(0, width)
            y = random.randint(0, 12)
        elif edge == "bottom":
            x = random.randint(0, width)
            y = random.randint(height - 12, height)
        elif edge == "left":
            x = random.randint(0, 12)
            y = random.randint(0, height)
        else:
            x = random.randint(width - 12, width)
            y = random.randint(0, height)

        radius = random.randint(1, 3)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(235, 235, 235))

    return worn


def add_stains(image: Image.Image, amount: int) -> Image.Image:
    # Creamos manchas semitransparentes para simular suciedad o daño.
    stained = image.convert("RGBA")
    overlay = Image.new("RGBA", stained.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    width, height = stained.size

    for _ in range(amount):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(8, 25)

        color = random.choice([
            (120, 90, 60, 60),
            (80, 80, 80, 50),
            (160, 120, 70, 45),
        ])

        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)

    combined = Image.alpha_composite(stained, overlay).convert("RGB")
    return combined


def create_played_image(image: Image.Image) -> Image.Image:
    # Played simula una carta usada con desgaste moderado.
    edited = ImageEnhance.Color(image).enhance(random.uniform(0.85, 0.95))
    edited = add_scratches(edited, amount=8, intensity=220)
    edited = add_border_wear(edited, amount=45)
    edited = add_stains(edited, amount=2)
    return edited


def create_damaged_image(image: Image.Image) -> Image.Image:
    # Damaged simula una carta con desgaste fuerte y defectos visibles.
    edited = ImageEnhance.Color(image).enhance(random.uniform(0.55, 0.75))
    edited = ImageEnhance.Contrast(edited).enhance(random.uniform(0.75, 0.9))
    edited = add_scratches(edited, amount=25, intensity=240)
    edited = add_border_wear(edited, amount=120)
    edited = add_stains(edited, amount=6)
    edited = edited.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.2, 0.6)))
    return edited


def save_image(image: Image.Image, label: str, card_id: str) -> None:
    # Guardamos cada imagen dentro de la carpeta de su clase.
    label_dir = OUTPUT_DIR / label
    label_dir.mkdir(parents=True, exist_ok=True)

    output_path = label_dir / f"{card_id}_{label}.jpg"
    image.save(output_path, format="JPEG", quality=90)


def generate_dataset(limit: int = 20) -> None:
    # Funcion principal que genera imagenes sinteticas para cada carta.
    cards = load_card_sample(limit=limit)

    for _, card in cards.iterrows():
        card_id = card["id"]
        image_url = card["image_large"]

        print(f"Processing {card_id}...")

        original = download_image(image_url)
        original = resize_image(original)

        synthetic_images = {
            "mint": create_mint_image(original),
            "played": create_played_image(original),
            "damaged": create_damaged_image(original),
        }

        for label, synthetic_image in synthetic_images.items():
            save_image(synthetic_image, label=label, card_id=card_id)

    print("Synthetic dataset generated successfully.")


if __name__ == "__main__":
    generate_dataset(limit=40)