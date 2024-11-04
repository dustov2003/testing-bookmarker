# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

from asyncio import get_event_loop_policy
from os import environ
from types import SimpleNamespace
from uuid import uuid4

import pytest
from alembic.command import upgrade
from alembic.config import Config
from httpx import AsyncClient
from mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from tests.utils import make_alembic_config

import bookmarker.utils as utils_module
from bookmarker.__main__ import get_app
from bookmarker.config.utils import get_settings
from bookmarker.db.connection import SessionManager
from bookmarker.db.models import Bookmark, User, Tag
from bookmarker.schemas.auth.registration import RegistrationForm
from bookmarker.utils.user import create_access_token, get_current_user


@pytest.fixture(scope="session")
def event_loop():
    """
    Creates event loop for tests.
    """
    policy = get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def postgres() -> str:
    """
    Создает временную БД для запуска теста.
    """
    settings = get_settings()

    tmp_name = ".".join([uuid4().hex, "pytest"])
    settings.POSTGRES_DB = tmp_name
    environ["POSTGRES_DB"] = tmp_name

    tmp_url = settings.database_uri_sync
    if not database_exists(tmp_url):
        create_database(tmp_url)

    try:
        yield settings.database_uri
    finally:
        drop_database(tmp_url)


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    upgrade(cfg, "head")


async def run_async_upgrade(config: Config, database_uri: str):
    async_engine = create_async_engine(database_uri, echo=True)
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, config)


@pytest.fixture
def alembic_config(postgres) -> Config:
    """
    Создает файл конфигурации для alembic.
    """
    cmd_options = SimpleNamespace(config="bookmarker/db/", name="alembic", pg_url=postgres, raiseerr=False, x=None)
    return make_alembic_config(cmd_options)


@pytest.fixture
def alembic_engine():
    """
    Override this fixture to provide pytest-alembic powered tests with a database handle.
    """
    settings = get_settings()
    return create_async_engine(settings.database_uri_sync, echo=True)


@pytest.fixture
async def migrated_postgres(postgres, alembic_config: Config):
    """
    Проводит миграции.
    """
    await run_async_upgrade(alembic_config, postgres)


@pytest.fixture
async def client(migrated_postgres, manager: SessionManager = SessionManager()) -> AsyncClient:
    """
    Returns a client that can be used to interact with the application.
    """
    app = get_app()
    manager.refresh()  # без вызова метода изменения конфига внутри фикстуры postgres не подтягиваются в класс
    utils_module.check_website_exist = AsyncMock(return_value=(True, "Status code < 400"))
    yield AsyncClient(app=app, base_url="http://test")


@pytest.fixture
async def engine_async(postgres) -> AsyncEngine:
    engine = create_async_engine(postgres, future=True)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory_async(engine_async) -> sessionmaker:
    return sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def session(session_factory_async) -> AsyncSession:
    async with session_factory_async() as session:
        yield session


@pytest.fixture
async def data_sample_user(session) -> User:
    """
    Creates minimum data sample for tests.
    """
    new_object = User(
        username="string", password=RegistrationForm.validate_password("striiiing"), email="user@example.com"
    )
    session.add(new_object)
    await session.commit()
    await session.refresh(new_object)
    return new_object


@pytest.fixture
async def jwt_token(data_sample_user) -> str:
    return create_access_token(data={"sub": data_sample_user.username})


@pytest.fixture
async def data_sample_bookmark(session, jwt_token) -> Bookmark:
    tag = Tag(name="example")
    session.add(tag)
    user = await get_current_user(session, jwt_token)
    new_object = Bookmark(title="Яндекс — быстрый поиск в интернете", link="https://ya.ru/", owner_id=user.id, tag=tag.name)
    session.add(new_object)
    new_object = Bookmark(title="Google", link="https://google.com/", owner_id=user.id, tag=tag.name)
    session.add(new_object)
    await session.commit()
    await session.refresh(new_object)
    return new_object


@pytest.fixture
async def auth_header(jwt_token):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    return headers
