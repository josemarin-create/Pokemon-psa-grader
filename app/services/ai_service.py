import os
import numpy as np
from io import BytesIO
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# 1. Apuntar al modelo físico
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "models", "modelo_pokemon.h5")

# 2. Cargar el modelo en memoria (se ejecuta solo una vez al arrancar la API)
print("Cargando modelo de IA en memoria... Esto puede tardar unos segundos.")
try:
    model = load_model(MODEL_PATH)
    print("Modelo cargado con éxito.")
except Exception as e:
    model = None
    print(f"⚠️ ERROR CRÍTICO: No se pudo cargar el modelo. ¿Está en {MODEL_PATH}?\n{e}")

# Estas clases DEBEN estar en el mismo orden alfabético que generó Colab
CLASS_NAMES = ['damaged', 'mint', 'played']

def predict_condition(image_bytes: bytes) -> dict:
    """Recibe los bytes de la imagen, la procesa y devuelve la predicción."""
    if model is None:
        raise RuntimeError("El modelo no está disponible.")

    # 1. Abrir imagen en memoria y forzar formato RGB (por si suben un PNG transparente)
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    
    # 2. Redimensionar al tamaño estricto de MobileNetV2
    img = img.resize((224, 224))
    
    # 3. Convertir a matriz matemática y aplicar el preprocesado oficial de MobileNet
    img_array = np.array(img, dtype=np.float32)
    img_array = np.expand_dims(img_array, axis=0) # Convertir a lote (batch) de 1
    img_array = preprocess_input(img_array)
    
    # 4. Magia negra (Predicción)
    predictions = model.predict(img_array)
    predicted_idx = np.argmax(predictions[0])
    confidence = float(np.max(predictions[0]))
    
    return {
        "condition": CLASS_NAMES[predicted_idx],
        "confidence": confidence
    }