from typing import Any

import psycopg
from psycopg.rows import dict_row

from lab4.domain import Product

COLS = "id, sku, name, price::float8 AS price, category_id"


def _to_product(row: dict[str, Any]) -> Product:
    return Product(**row)


class PgProductRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def _conn(self) -> psycopg.Connection[dict[str, Any]]:
        return psycopg.connect(self._dsn, row_factory=dict_row)

    def list(self) -> list[Product]:
        with self._conn() as conn:
            rows = conn.execute(f"SELECT {COLS} FROM products ORDER BY id").fetchall()
        return [_to_product(r) for r in rows]

    def get(self, product_id: int) -> Product | None:
        with self._conn() as conn:
            row = conn.execute(
                f"SELECT {COLS} FROM products WHERE id = %s", (product_id,)
            ).fetchone()
        return _to_product(row) if row else None

    def create(self, product: Product) -> Product:
        with self._conn() as conn:
            row = conn.execute(
                "INSERT INTO products (sku, name, price, category_id) "
                f"VALUES (%s, %s, %s, %s) RETURNING {COLS}",
                (product.sku, product.name, product.price, product.category_id),
            ).fetchone()
        assert row is not None
        return _to_product(row)

    def update(self, product_id: int, product: Product) -> Product | None:
        with self._conn() as conn:
            row = conn.execute(
                "UPDATE products SET sku=%s, name=%s, price=%s, category_id=%s "
                f"WHERE id=%s RETURNING {COLS}",
                (
                    product.sku,
                    product.name,
                    product.price,
                    product.category_id,
                    product_id,
                ),
            ).fetchone()
        return _to_product(row) if row else None

    def delete(self, product_id: int) -> bool:
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM products WHERE id = %s", (product_id,))
            return cur.rowcount > 0
