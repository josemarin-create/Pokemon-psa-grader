from fastapi import APIRouter, HTTPException, Query

from app.schemas.card import CardResponse, CardSearchItem
from app.services.pokemon_tcg_service import get_card_by_id, search_cards_by_name


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
