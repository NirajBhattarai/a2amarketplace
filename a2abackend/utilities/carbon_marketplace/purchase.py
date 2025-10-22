from decimal import Decimal
from typing import Optional, Tuple
from .db import get_db_connection


def purchase_credits(company_id: int, user_account: str, amount: Decimal, payment_tx_id: Optional[str] = None) -> Tuple[bool, str]:
    """
    Deduct 'amount' credits from company's current_credit, add to sold_credit,
    and record a purchase row. Returns (success, message).
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Lock row for update
            cur.execute("SELECT current_credit, offer_price FROM company_credit WHERE company_id=%s FOR UPDATE", (company_id,))
            row = cur.fetchone()
            if not row:
                return False, "Company credit not found"
            current_credit, offer_price = row
            if current_credit < amount:
                return False, "Insufficient company credit"

            # Update balances
            cur.execute(
                """
                UPDATE company_credit
                SET current_credit = current_credit - %s,
                    sold_credit = sold_credit + %s
                WHERE company_id = %s
                """,
                (amount, amount, company_id),
            )

            total_price = (offer_price or Decimal("0.00")) * amount
            # Record purchase
            cur.execute(
                """
                INSERT INTO credit_purchase (company_id, user_account, amount, price_per_credit, total_price, payment_tx_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (company_id, user_account, amount, offer_price or Decimal("0.00"), total_price, payment_tx_id),
            )

        return True, "Purchase recorded"
    finally:
        conn.close()


