import os
from decimal import Decimal
from .db import get_db_connection, run_sql_file


SEED_COMPANIES = [
    {
        "company_name": "GreenEarth Ltd",
        "address": "123 Forest Road",
        "website": "https://greenearth.example",
        "location": "USA",
        "wallet_address": "0.0.111111",
        "total_credit": Decimal("10000.00"),
        "current_credit": Decimal("8000.00"),
        "offer_price": Decimal("12.50"),
    },
    {
        "company_name": "BlueSky Carbon",
        "address": "456 Sky Ave",
        "website": "https://bluesky.example",
        "location": "EU",
        "wallet_address": "0.0.222222",
        "total_credit": Decimal("20000.00"),
        "current_credit": Decimal("15000.00"),
        "offer_price": Decimal("11.75"),
    },
    {
        "company_name": "EcoFuture Corp",
        "address": "789 Future Blvd",
        "website": "https://ecofuture.example",
        "location": "APAC",
        "wallet_address": "0.0.333333",
        "total_credit": Decimal("5000.00"),
        "current_credit": Decimal("4200.00"),
        "offer_price": Decimal("13.20"),
    },
]


def main():
    conn = get_db_connection()
    try:
        # Create schema
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        run_sql_file(conn, schema_path)

        with conn.cursor() as cur:
            # Clear existing data
            cur.execute("DELETE FROM credit_purchase;")
            cur.execute("DELETE FROM company_credit;")
            cur.execute("DELETE FROM company;")

            # Insert companies and credits
            for c in SEED_COMPANIES:
                cur.execute(
                    """
                    INSERT INTO company (company_name, address, website, location, wallet_address)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING company_id
                    """,
                    (
                        c["company_name"],
                        c["address"],
                        c["website"],
                        c["location"],
                        c["wallet_address"],
                    ),
                )
                company_id = cur.fetchone()[0]

                cur.execute(
                    """
                    INSERT INTO company_credit (company_id, total_credit, current_credit, sold_credit, offer_price)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        company_id,
                        c["total_credit"],
                        c["current_credit"],
                        Decimal("0.00"),
                        c["offer_price"],
                    ),
                )

        print("Seed completed successfully")
    finally:
        conn.close()


if __name__ == "__main__":
    main()


