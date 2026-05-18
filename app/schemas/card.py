from pydantic import BaseModel


class CardPrice(BaseModel):
    # Precio medio de venta en Cardmarket, si existe.
    average_sell_price: float | None = None

    # Precio de tendencia en Cardmarket, usado como alternativa.
    trend_price: float | None = None

    # Precio elegido por nuestra API como precio base.
    selected_price: float | None = None

    # Campo que explica de donde viene el precio seleccionado.
    price_source: str


class CardResponse(BaseModel):
    # ID oficial de la carta en Pokemon TCG API.
    id: str

    # Nombre de la carta, por ejemplo "Charizard".
    name: str

    # Nombre del set o coleccion.
    set_name: str

    # Rareza de la carta si la API la proporciona.
    rarity: str | None = None

    # URL de la imagen oficial de la carta.
    image_url: str | None = None

    # Informacion de precios ya normalizada.
    price: CardPrice


class CardSearchItem(BaseModel):
    # Resultado resumido para listados de busqueda.
    id: str
    name: str
    set_name: str
    rarity: str | None = None
    image_url: str | None = None