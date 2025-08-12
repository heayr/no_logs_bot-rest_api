# db/crud/transaction_crud.py
import logging
from datetime import datetime
from db.session import get_connection
import sqlite3
from typing import Optional, Dict

async def save_pending_transaction(telegram_id: int, transaction_id: str, amount: float, days: int, payment_id: str = None) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO transactions (transaction_id, telegram_id, amount, days, status, created_at, updated_at, payment_provider, payment_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transaction_id,
                telegram_id,
                amount,
                days,
                "pending",
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat(),
                "yookassa",
                payment_id
            )
        )
        conn.commit()
        conn.close()
        logging.debug(f"Транзакция сохранена: transaction_id={transaction_id}, tg_id={telegram_id}, payment_id={payment_id}")
        return True
    except sqlite3.IntegrityError as e:
        logging.error(f"Ошибка целостности при сохранении транзакции для tg_id={telegram_id}: {e}", exc_info=True)
        return False
    except Exception as e:
        logging.error(f"Ошибка при сохранении транзакции для tg_id={telegram_id}: {e}", exc_info=True)
        return False

async def get_confirmed_transaction(telegram_id: int) -> Optional[Dict]:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT transaction_id, telegram_id, amount, days, status FROM transactions WHERE telegram_id = ? AND status = ?",
            (telegram_id, "completed")
        )
        transaction = cursor.fetchone()
        conn.close()
        if transaction:
            return {
                "transaction_id": transaction[0],
                "telegram_id": transaction[1],
                "amount": transaction[2],
                "days": transaction[3],
                "status": transaction[4]
            }
        logging.debug(f"Транзакция для tg_id={telegram_id} не найдена")
        return None
    except Exception as e:
        logging.error(f"Ошибка при получении транзакции для tg_id={telegram_id}: {e}", exc_info=True)
        return None

async def confirm_transaction(transaction_id: str) -> Optional[Dict]:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE transactions SET status = ?, updated_at = ? WHERE transaction_id = ? AND status = ?",
            ("completed", datetime.utcnow().isoformat(), transaction_id, "pending")
        )
        affected_rows = cursor.rowcount
        conn.commit()
        cursor.execute(
            "SELECT transaction_id, telegram_id, amount, days, status FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        )
        transaction = cursor.fetchone()
        conn.close()
        if transaction and affected_rows > 0:
            return {
                "transaction_id": transaction[0],
                "telegram_id": transaction[1],
                "amount": transaction[2],
                "days": transaction[3],
                "status": transaction[4]
            }
        logging.error(f"Транзакция {transaction_id} не найдена или уже подтверждена")
        return None
    except Exception as e:
        logging.error(f"Ошибка при подтверждении транзакции {transaction_id}: {e}", exc_info=True)
        return None