import psycopg

DSN = "postgresql://postgres:postgres@localhost:5432/postgres"

SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id serial PRIMARY KEY,
    name text UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS suppliers (
    id serial PRIMARY KEY,
    name text NOT NULL,
    email text UNIQUE NOT NULL,
    phone text NOT NULL
);
CREATE TABLE IF NOT EXISTS products (
    id serial PRIMARY KEY,
    sku text UNIQUE NOT NULL,
    name text NOT NULL,
    price numeric(10,2) NOT NULL CHECK (price >= 0),
    category_id int NOT NULL REFERENCES categories(id)
);
CREATE TABLE IF NOT EXISTS product_suppliers (
    product_id int REFERENCES products(id) ON DELETE CASCADE,
    supplier_id int REFERENCES suppliers(id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, supplier_id)
);
"""


def main() -> None:
    with psycopg.connect(DSN) as conn:
        conn.execute(SCHEMA)
        if conn.execute("SELECT count(*) FROM products").fetchone() != (0,):
            print("Already initialised")
            return

        cats = [
            "Холодильники",
            "Пральні машини",
            "Чайники",
            "Пилососи",
            "Мікрохвильовки",
        ]
        conn.cursor().executemany(
            "INSERT INTO categories (name) VALUES (%s)", [(c,) for c in cats]
        )
        conn.cursor().executemany(
            "INSERT INTO suppliers (name, email, phone) VALUES (%s, %s, %s)",
            [
                (
                    f"Постачальник {i}",
                    f"supplier{i}@example.com",
                    f"+38050{1000000 + i}",
                )
                for i in range(1, 9)
            ],
        )
        conn.cursor().executemany(
            "INSERT INTO products (sku, name, price, category_id) VALUES (%s, %s, %s, %s)",
            [
                (f"ELE-{1000 + i}", f"Товар {i}", 500 + i * 37, i % 5 + 1)
                for i in range(1, 41)
            ],
        )
        conn.cursor().executemany(
            "INSERT INTO product_suppliers (product_id, supplier_id) VALUES (%s, %s)",
            [(p, (p + k) % 8 + 1) for p in range(1, 41) for k in (0, 3)],
        )
    print("Done")


if __name__ == "__main__":
    main()
