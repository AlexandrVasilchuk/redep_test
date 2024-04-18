import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    declared_attr,
    mapped_column,
    sessionmaker,
)

load_dotenv()


class PreBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


Base = declarative_base(cls=PreBase)
engine = create_async_engine(os.getenv("DB_URL"))
session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session():
    async with session_maker() as async_session:
        yield async_session


if __name__ == "__main__":
    while True:
        pass
