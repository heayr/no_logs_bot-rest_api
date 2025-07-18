# schemas/user.py
from pydantic import BaseModel, Field   
from datetime import datetime

class UserCreateResponse(BaseModel):
    uuid: str = Field(..., description="UUID клиента в Xray")
    link: str = Field(..., description="VLESS‑ссылка для клиента")
    expires_at: datetime = Field(..., description="UTC‑дата истечения теста")

class UserStats(BaseModel):
    total_users: int
    active_users: int
    expired_users: int
