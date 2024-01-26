import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from src.configs import (DB_HOST_TEST, DB_NAME, DB_PORT, POSTGRES_PASSWORD,
                         POSTGRES_USER)
from src.database import Base, get_db
from src.main import app

DATABASE_URL_TEST = (
    f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@'
    f'{DB_HOST_TEST}:{DB_PORT}/{DB_NAME}'
)

async_engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(
    async_engine_test,
    class_=AsyncSession,
    expire_on_commit=False
)
Base.bind = async_engine_test


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with async_engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop():
    try:
        loop = asyncio.get_event_loop_policy().new_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='session')
def fixture_new_menu():
    """Фикстура для меню."""

    return {}


@pytest.fixture(scope='session')
def fixture_new_submenu():
    """Фикстура для подменю."""

    return {}


@pytest.fixture(scope='session')
def fixture_new_dish():
    """Фикстура для нового блюда."""

    return {}