# bot/handlers/test_config.py
import logging
from core.config import settings
from aiogram import Router, types
from bot.services.user_config_service import create_test_user

test_config_handler = Router()


@test_config_handler.message(lambda m: m.text == "🎁 Получить тест")
async def handle_test_request(message: types.Message):
    try:
        config_link, expires_days, error = await create_test_user(
            message.from_user.id,
            minutes=settings.TEST_MINUTES,
            return_days=True
        )

        if error:
            await message.answer(error)
        elif config_link and expires_days is not None:
            response = (
                f"🔒 Ваш тестовый VPN-конфиг:\n\n"
                f"{config_link}\n\n"
                f"⏳ Срок действия: {expires_days} дней\n\n"
                f"Для подключения используйте любой клиент V2RayN."
            )
            if str(message.from_user.id) in map(str, settings.ADMIN_IDS):  # исправлено
                response += "\n\n⚙️ Вы получили конфиг в обход ограничений (режим администратора)"
            await message.answer(response)
        else:
            await message.answer("Не удалось создать конфиг. Попробуйте позже.")

    except Exception as e:
        logging.error(f"Ошибка в handle_test_request: {str(e)}", exc_info=True)
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
