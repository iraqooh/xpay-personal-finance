from pydantic import BaseModel
from .user import UserRead

class AuthResponse(BaseModel):
    user: UserRead
    access_token: str
    token_type: str = "bearer"