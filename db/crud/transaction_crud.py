# db/crud/transaction_crud.py



import sqlite3
from datetime import datetime
import logging
from core.config import settings

def save_pending_transaction(telegram_id: int, order_id: str, amount: float, days: int, payment_id: str) -> bool:
    """
    Сохраняет транзакцию со статусом 'pending' в базу данных.
    """
    try:
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        current_time = datetime.now().isoformat()
        cursor.execute(
            """
            INSERT INTO transactions (transaction_id, telegram_id, amount, days, status, created_at, updated_at, payment_provider, payment_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (order_id, telegram_id, amount, days, "pending", current_time, current_time, "yookassa", payment_id)
        )
        conn.commit()
        conn.close()
        logging.info(f"Транзакция сохранена: transaction_id={order_id}, telegram_id={telegram_id}, payment_id={payment_id}")
        return True
    except Exception as e:
        logging.error(f"Ошибка при сохранении транзакции: transaction_id={order_id}, telegram_id={telegram_id}, {str(e)}")
        return False

def get_confirmed_transaction(telegram_id: int) -> dict | None:
    """
    Получает подтверждённую транзакцию (status='succeeded') для пользователя.
    """
    try:
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT transaction_id, telegram_id, amount, days, status, created_at, updated_at, payment_provider, payment_id
            FROM transactions WHERE telegram_id = ? AND status = ?
            """,
            (telegram_id, "succeeded")
        )
        transaction = cursor.fetchone()
        conn.close()
        if transaction:
            return {
                "transaction_id": transaction[0],
                "telegram_id": transaction[1],
                "amount": transaction[2],
                "days": transaction[3],
                "status": transaction[4],
                "created_at": transaction[5],
                "updated_at": transaction[6],
                "payment_provider": transaction[7],
                "payment_id": transaction[8]
            }
        return None
    except Exception as e:
        logging.error(f"Ошибка при получении подтверждённой транзакции: telegram_id={telegram_id}, {str(e)}")
        return None

def get_transaction_by_id(transaction_id: str) -> dict | None:
    """
    Получает транзакцию по ID.
    """
    try:
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT transaction_id, telegram_id, amount, days, status, created_at, updated_at, payment_provider, payment_id
            FROM transactions WHERE transaction_id = ?
            """,
            (transaction_id,)
        )
        transaction = cursor.fetchone()
        conn.close()
        if transaction:
            return {
                "transaction_id": transaction[0],
                "telegram_id": transaction[1],
                "amount": transaction[2],
                "days": transaction[3],
                "status": transaction[4],
                "created_at": transaction[5],
                "updated_at": transaction[6],
                "payment_provider": transaction[7],
                "payment_id": transaction[8]
            }
        return None
    except Exception as e:
        logging.error(f"Ошибка при получении транзакции: transaction_id={transaction_id}, {str(e)}")
        return None

def update_transaction_status(transaction_id: str, status: str) -> bool:
    """
    Обновляет статус транзакции.
    """
    try:
        conn = sqlite3.connect(settings.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE transactions SET status = ?, updated_at = ? WHERE transaction_id = ?
            """,
            (status, datetime.now().isoformat(), transaction_id)
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        if updated:
            logging.info(f"Статус транзакции обновлён: transaction_id={transaction_id}, status={status}")
        return updated
    except Exception as e:
        logging.error(f"Ошибка при обновлении статуса транзакции: transaction_id={transaction_id}, {str(e)}")
        return False