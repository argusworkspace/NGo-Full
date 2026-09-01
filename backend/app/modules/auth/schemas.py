from pydantic import BaseModel, EmailStr
from typing import Literal


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    # Kept snake_case (unlike the rest of this API's camelCase wire format):
    # this is the OAuth2-style token pair the frontend's AuthTokens type and
    # localStorage key ("access_token") already integrate against.
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: Literal["ADMIN", "VOLUNTEER"]

    model_config = {"from_attributes": True}
