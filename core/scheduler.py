# core/scheduler.py (или tasks/cleaner.py)

import asyncio
from services.user_cleanup_service import delete_expired_users

async def expired_user_cleaner():
    while True:
        delete_expired_users()
        await asyncio.sleep(3600)  # раз в час