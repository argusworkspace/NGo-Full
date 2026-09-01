import uuid
from typing import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, pool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.modules.auth.models import User

# NullPool: each test gets a brand new asyncpg connection bound to that
# test's own event loop, instead of reusing a pooled connection created in a
# different (now-closed) event loop from a previous test.
test_engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=pool.NullPool,
    connect_args={"ssl": True} if "neon.tech" in settings.DATABASE_URL else {},
)


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """A session bound to a single connection wrapped in an outer transaction
    that's always rolled back, so nothing a test does (including calls the
    app makes via `commit()`) survives the test."""
    async with test_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()
        session_factory = async_sessionmaker(bind=conn, expire_on_commit=False, class_=AsyncSession)
        session = session_factory()

        @event.listens_for(session.sync_session, "after_transaction_end")
        def _restart_savepoint(sess, transaction):
            if conn.closed:
                return
            if not conn.sync_connection.in_nested_transaction():
                conn.sync_connection.begin_nested()

        try:
            yield session
        finally:
            await session.close()
            await conn.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    user = User(
        name="Test Admin",
        email=_unique_email("admin"),
        hashed_password=hash_password("Admin@123"),
        role="ADMIN",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def normal_user(db_session: AsyncSession) -> User:
    user = User(
        name="Test User",
        email=_unique_email("user"),
        hashed_password=hash_password("User@123"),
        role="VOLUNTEER",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
def admin_token(admin_user: User) -> str:
    return create_access_token(admin_user.id, admin_user.role)


@pytest_asyncio.fixture
def user_token(normal_user: User) -> str:
    return create_access_token(normal_user.id, normal_user.role)


@pytest_asyncio.fixture
def auth_headers():
    def _make(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    return _make
