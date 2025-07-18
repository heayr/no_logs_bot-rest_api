# api/routes/users.py

from fastapi import APIRouter, HTTPException, status
from schemas.user import UserCreateResponse
from bot.services.user_config_service import create_test_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/test", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_test():
    try:
        data = await create_test_user()
        return UserCreateResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
