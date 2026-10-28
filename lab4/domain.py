from dataclasses import dataclass


@dataclass
class Product:
    sku: str
    name: str
    price: float
    category_id: int
    id: int | None = None
