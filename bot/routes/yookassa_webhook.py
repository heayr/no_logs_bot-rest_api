#bot/routes/yookassa_webhook.py




from fastapi import APIRouter, Request, BackgroundTasks
from bot.services.yookassa_service import capture_payment
from bot.services.user_config_service import handle_payment_callback
from bot.bot import bot
import logging

router = APIRouter()

@router.post("/webhook/yookassa")
async def handle_yookassa_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Обрабатывает вебхуки от ЮKassa для подтверждения платежей и создания конфигов.
    """
    try:
        data = await request.json()
        logging.info(f"Получен запрос на /webhook/yookassa: {data}")
        
        payment_data = data.get('object', {})
        payment_status = payment_data.get('status')
        payment_id = payment_data.get('id')
        amount = payment_data.get('amount', {}).get('value')
        metadata = payment_data.get('metadata', {})
        telegram_id = metadata.get('telegram_id')
        order_id = metadata.get('order_id')
        
        logging.info(f"Обработка вебхука ЮKassa: payment_id={payment_id}, status={payment_status}, telegram_id={telegram_id}, order_id={order_id}")

        if not telegram_id or not order_id:
            logging.error(f"Некорректные метаданные: telegram_id={telegram_id}, order_id={order_id}")
            return {"status": "error", "message": "Invalid metadata"}

        # Автоподтверждение платежа
        if payment_status == "waiting_for_capture":
            logging.info(f"Автоподтверждение платежа: payment_id={payment_id}")
            capture_success = await capture_payment(payment_id, float(amount) if amount else 200.00)
            if capture_success:
                logging.info(f"Платёж {payment_id} успешно захвачен")
                background_tasks.add_task(handle_payment_callback, data, bot)
                return {"status": "success", "message": "Payment captured"}
            else:
                logging.error(f"Не удалось захватить платёж: payment_id={payment_id}")
                return {"status": "error", "message": "Capture failed"}
        
        # Обработка уже подтверждённых платежей
        elif payment_status == "succeeded":
            logging.info(f"Платёж уже подтверждён: payment_id={payment_id}")
            background_tasks.add_task(handle_payment_callback, data, bot)
            return {"status": "success", "message": "Payment already succeeded"}
        
        # Обработка отменённых платежей
        elif payment_status == "canceled":
            logging.info(f"Платёж отменён: payment_id={payment_id}")
            return {"status": "info", "message": "Payment canceled"}
        
        # Обработка других статусов
        else:
            logging.info(f"Платёж в статусе {payment_status}, пропускаем обработку")
            return {"status": "info", "message": f"Payment status: {payment_status}"}
            
    except Exception as e:
        logging.error(f"Ошибка обработки вебхука ЮKassa: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}