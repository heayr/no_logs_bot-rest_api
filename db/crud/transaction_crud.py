# /db/crud/transaction_crud.py

import logging
from datetime import datetime
from db.session import get_connection
from core.config import settings
import sqlite3

def get_connection():
    return sqlite3.connect(settings.DATABASE_PATH)

def save_pending_transaction(telegram_id: int, transaction_id: str, amount: float, days: int) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        if not cursor.fetchone():
            raise Exception("Таблица transactions не существует")
        cursor.execute(
            """
            INSERT INTO transactions (transaction_id, telegram_id, amount, days, status, created_at, updated_at, payment_provider)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transaction_id,
                telegram_id,
                amount,
                days,
                "pending",
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat(),
                "yookassa"
            )
        )
        conn.commit()
        conn.close()
        logging.debug(f"Транзакция сохранена: transaction_id={transaction_id}, tg_id={telegram_id}")
        return True
    except Exception as e:
        logging.error(f"Ошибка при сохранении транзакции для tg_id={telegram_id}: {e}")
        return False

def get_confirmed_transaction(telegram_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT transaction_id, telegram_id, amount, days, status FROM transactions WHERE telegram_id = ? AND status = ?",
            (telegram_id, "completed")
        )
        transaction = cursor.fetchone()
        conn.close()
        logging.debug(f"Получена транзакция для tg_id={telegram_id}: {transaction}")
        return transaction
    except Exception as e:
        logging.error(f"Ошибка при получении транзакции для tg_id={telegram_id}: {e}")
        return None

def confirm_transaction(transaction_id: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE transactions SET status = ?, updated_at = ? WHERE transaction_id = ? AND status = ?",
            ("completed", datetime.utcnow().isoformat(), transaction_id, "pending")
        )
        conn.commit()
        cursor.execute(
            "SELECT transaction_id, telegram_id, amount, days, status FROM transactions WHERE transaction_id = ?",
            (transaction_id,)
        )
        transaction = cursor.fetchone()
        conn.close()
        logging.debug(f"Транзакция подтверждена: transaction_id={transaction_id}, result={transaction}")
        return transaction
    except Exception as e:
        logging.error(f"Ошибка при подтверждении транзакции {transaction_id}: {e}")
        return None