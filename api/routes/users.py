# api/routes/users.py

from fastapi import APIRouter, HTTPException, status
from schemas.user import UserCreateResponse
from bot.services.user_config_service import create_test_user
from db.crud.user_crud import delete_user_by_uuid
import traceback
from bot.services.xray_service import remove_client


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/test", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_test():
    try:
        data = await create_test_user()
        return UserCreateResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{uuid}")
def delete_user(uuid: str):
    try:
        removed_from_xray = remove_client(uuid)
        removed_from_db = delete_user_by_uuid(uuid)

        if not removed_from_xray and not removed_from_db:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        return {
            "status": "ok",
            "removed_from_xray": removed_from_xray,
            "removed_from_db": removed_from_db,
        }
    except Exception as e:
        import logging
        logging.error(f"Ошибка в delete_user: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")