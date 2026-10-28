from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI, HTTPException, Response
from pydantic import BaseModel, Field, field_validator

from lab4.domain import Product
from lab4.pg_repository import PgProductRepository
from lab4.repository import ProductRepository
from lab4.validators import validate_sku

DSN = "postgresql://postgres:postgres@localhost:5432/postgres"

app = FastAPI(title="Lab 4 REST API")


def get_repo() -> ProductRepository:
    return PgProductRepository(DSN)


Repo = Annotated[ProductRepository, Depends(get_repo)]


class ProductIn(BaseModel):
    sku: str
    name: str = Field(min_length=1, max_length=255)
    price: float = Field(ge=0)
    category_id: int

    @field_validator("sku")
    @classmethod
    def check_sku(cls, v: str) -> str:
        return validate_sku(v)


class ProductOut(ProductIn):
    id: int


def _dom(data: ProductIn) -> Product:
    return Product(**data.model_dump())


@app.get("/products", response_model=list[ProductOut])
def list_products(repo: Repo) -> list[Product]:
    return repo.list()


@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, repo: Repo) -> Product:
    product = repo.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Not found")
    return product


@app.post("/products", response_model=ProductOut, status_code=201)
def create_product(data: ProductIn, repo: Repo) -> Product:
    try:
        return repo.create(_dom(data))
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="SKU already exists")
    except psycopg.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="Unknown category_id")


@app.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductIn, repo: Repo) -> Product:
    try:
        product = repo.update(product_id, _dom(data))
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="SKU already exists")
    except psycopg.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="Unknown category_id")
    if product is None:
        raise HTTPException(status_code=404, detail="Not found")
    return product


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, repo: Repo) -> Response:
    if not repo.delete(product_id):
        raise HTTPException(status_code=404, detail="Not found")
    return Response(status_code=204)
