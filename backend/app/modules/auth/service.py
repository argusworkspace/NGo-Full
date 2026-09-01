from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import hash_password, verify_password, create_access_token
from app.shared.exceptions import UnauthorizedException, ConflictException
from .models import User
from .schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse


async def login(data: LoginRequest, db: AsyncSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise UnauthorizedException("Invalid credentials")
    return TokenResponse(access_token=create_access_token(user.id, user.role))


async def register(data: RegisterRequest, db: AsyncSession) -> UserResponse:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise ConflictException("Email already registered")

    user = User(name=data.name, email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    await db.flush()
    return UserResponse.model_validate(user)
