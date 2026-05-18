import requests

from app.core.config import settings


# URL base oficial de la Pokemon TCG API.
BASE_URL = "https://api.pokemontcg.io/v2"


def _build_headers() -> dict:
    # La API key es opcional, pero mejora los limites de uso si la tenemos.
    if settings.pokemon_tcg_api_key:
        return {"X-Api-Key": settings.pokemon_tcg_api_key}

    return {}


def _select_market_price(card_data: dict) -> dict:
    # Cardmarket suele dar precios en EUR.
    prices = card_data.get("cardmarket", {}).get("prices", {})

    average_sell_price = prices.get("averageSellPrice")
    trend_price = prices.get("trendPrice")

    # Priorizamos precio medio de venta porque representa ventas reales recientes.
    if average_sell_price is not None:
        selected_price = average_sell_price
        price_source = "cardmarket.averageSellPrice"

    # Si no hay precio medio, usamos precio de tendencia como alternativa.
    elif trend_price is not None:
        selected_price = trend_price
        price_source = "cardmarket.trendPrice"

    # Si no hay ningun precio disponible, lo dejamos como None.
    else:
        selected_price = None
        price_source = "not_available"

    return {
        "average_sell_price": average_sell_price,
        "trend_price": trend_price,
        "selected_price": selected_price,
        "price_source": price_source,
    }


def _normalize_card(card_data: dict) -> dict:
    # Convertimos la respuesta grande de la API externa en un formato simple.
    images = card_data.get("images", {})

    return {
        "id": card_data["id"],
        "name": card_data["name"],
        "set_name": card_data.get("set", {}).get("name", "Unknown set"),
        "rarity": card_data.get("rarity"),
        "image_url": images.get("large") or images.get("small"),
        "price": _select_market_price(card_data),
    }


def get_card_by_id(card_id: str) -> dict | None:
    # Busca una carta concreta por su ID oficial.
    url = f"{BASE_URL}/cards/{card_id}"

    response = requests.get(url, headers=_build_headers(), timeout=10)

    if response.status_code == 404:
        return None

    response.raise_for_status()

    card_data = response.json()["data"]
    return _normalize_card(card_data)


def search_cards_by_name(name: str, page_size: int = 10) -> list[dict]:
    # Busca cartas por nombre. El asterisco permite busqueda parcial.
    url = f"{BASE_URL}/cards"
    params = {
        "q": f'name:"{name}*"',
        "pageSize": page_size,
        "orderBy": "name",
    }

    response = requests.get(url, headers=_build_headers(), params=params, timeout=10)
    response.raise_for_status()

    cards = response.json().get("data", [])
    return [_normalize_card(card) for card in cards]