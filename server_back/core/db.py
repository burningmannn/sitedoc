import logging
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core import config

metadata_obj = MetaData()

database_name = config.settings.PS_DATABASE_NAME
database_driver = config.settings.PS_DRIVER
database_username = config.settings.PS_USERNAME
database_password = config.settings.PS_PASSWORD
database_host = config.settings.PS_HOST
database_dbname = config.settings.PS_TABLE_NAME

engine = create_async_engine(
    f"{database_name}+{database_driver}://{database_username}:{database_password}@{database_host}/{database_dbname}",
    echo=False)

session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    ...


async def get_async_session() -> AsyncSession:
    async with session_factory() as session:
        yield session


def connection(method):
    async def wrapper(*args, **kwargs):
        async with session_factory() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()
                logging.error(f'BD_ERROR: {e}')
                raise e
            finally:
                await session.close()

    return wrapper
