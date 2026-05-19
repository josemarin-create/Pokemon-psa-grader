from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from app.schemas.card import CardResponse, CardSearchItem, AppraisalResponse
from app.services.pokemon_tcg_service import get_card_by_id, search_cards_by_name
from app.services.ai_service import predict_condition


# Router principal para agrupar endpoints versionados.
router = APIRouter(prefix="/api/v1", tags=["cards"])


@router.get("/card/{card_id}", response_model=CardResponse)
def read_card(card_id: str):
    # Endpoint para buscar una carta por su ID oficial.
    card = get_card_by_id(card_id)

    if card is None:
        raise HTTPException(
            status_code=404,
            detail="Card not found. Check the Pokemon TCG card ID.",
        )

    return card


@router.get("/search", response_model=list[CardSearchItem])
def search_cards(
    name: str = Query(..., min_length=2, description="Pokemon card name to search"),
    page_size: int = Query(10, ge=1, le=20, description="Maximum number of results"),
):
    # Endpoint para buscar cartas por nombre.
    cards = search_cards_by_name(name=name, page_size=page_size)

    if not cards:
        raise HTTPException(
            status_code=404,
            detail="No cards found for this search.",
        )

    return cards


MULTIPLIERS = {
    "mint": 1.0,
    "played": 0.40,
    "damaged": 0.20
}

@router.post("/appraise", response_model=AppraisalResponse)
async def appraise_card(
    card_id: str = Form(..., description="ID de la carta en la PokeAPI (ej. base1-4)"),
    file: UploadFile = File(..., description="Foto de la carta Pokémon")
):
    """
    Endpoint maestro: Recibe una foto y un ID de carta.
    Devuelve la predicción de la IA y el precio ajustado.
    """
    # 1. Validar formato de imagen
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="El archivo debe ser JPG o PNG.")

    # 2. Consultar la API externa para sacar el precio base
    card = get_card_by_id(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Carta no encontrada en el mercado.")
    
    # Extraer el precio (si lo hay)
    base_price = card["price"]["selected_price"]

    # 3. Leer los bytes de la imagen y pasarlos a la IA
    image_bytes = await file.read()
    try:
        prediction = predict_condition(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la IA: {str(e)}")
    
    condition = prediction["condition"]
    multiplier = MULTIPLIERS.get(condition, 1.0)
    
    # 4. Matemáticas (Ajustar el precio)
    adjusted_price = None
    if base_price is not None:
        adjusted_price = round(base_price * multiplier, 2)

    # 5. Devolver el JSON final
    return AppraisalResponse(
        card_id=card["id"],
        card_name=card["name"],
        market_price=base_price,
        predicted_condition=condition,
        ai_confidence=prediction["confidence"],
        adjusted_price=adjusted_price,
        condition_multiplier=multiplier
    )