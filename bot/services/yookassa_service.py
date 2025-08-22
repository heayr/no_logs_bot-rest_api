#bot/services/yookassa_service.py


import logging
from yookassa import Configuration, Payment

# Настройка ЮKassa
Configuration.account_id = "1133698"
Configuration.secret_key = "test_XzPhDavE0PF5MfRT4zY22gdRU_K0PUsFGX-d8ZWrso0"

async def capture_payment(payment_id: str, amount: float = None) -> bool:
    """
    Подтверждает (захватывает) платеж в ЮKassa.
    """
    try:
        # Создаем объект для подтверждения платежа
        capture_request = {
            "amount": {
                "value": f"{amount:.2f}" if amount else "200.00",
                "currency": "RUB"
            }
        }

        # Выполняем подтверждение платежа
        payment = Payment.capture(payment_id, capture_request)
        
        if payment.status == 'succeeded':
            logging.info(f"Платёж {payment_id} успешно подтверждён")
            return True
        else:
            logging.warning(f"Платёж {payment_id} не подтверждён, статус: {payment.status}")
            return False
            
    except Exception as e:
        logging.error(f"Ошибка при подтверждении платежа {payment_id}: {e}")
        return False