from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import Base


class AbstractRepository(ABC):
    """Абстрактный класс репозитория.

    Определяет базовые методы для работы с базой данных.
    """

    @abstractmethod
    async def create_one(
        self, data: dict, session: AsyncSession, to_commit: bool
    ) -> None:
        """Создает новую запись в базе данных.

        Args:
            data (dict): Данные для создания новой записи.
            session (AsyncSession): Сессия SQLAlchemy для выполнения запроса.
            to_commit (bool): Флаг, указывающий нужно ли фиксировать изменения в базе данных.

        Returns:
            None
        """
        raise NotImplementedError

    @abstractmethod
    async def add_one(
        self, instance: Base, session: AsyncSession, to_commit: bool
    ) -> None:
        """Добавляет одну запись в базу данных.

        Args:
            instance (Base): Объект модели, который нужно добавить в базу данных.
            session (AsyncSession): Сессия SQLAlchemy для выполнения запроса.
            to_commit (bool): Флаг, указывающий нужно ли фиксировать изменения в базе данных.

        Returns:
            None
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_attr(
        self, attribute_name: str, attribute_value: Any, session: AsyncSession
    ) -> Any:
        """Возвращает запись по указанному атрибуту.

        Args:
            attribute_name (str): Название атрибута для поиска.
            attribute_value (Any): Значение атрибута для поиска.
            session (AsyncSession): Сессия SQLAlchemy для выполнения запроса.

        Returns:
            Any: Запись из базы данных.
        """
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, session: AsyncSession) -> list:
        """Возвращает все записи из базы данных.

        Args:
            session (AsyncSession): Сессия SQLAlchemy для выполнения запроса.

        Returns:
            list: Список всех записей из базы данных.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self, instance: Base, session: AsyncSession, to_commit: bool
    ) -> None:
        """Удаляет запись из базы данных.

        Args:
            instance (Base): Объект модели, который нужно удалить из базы данных.
            session (AsyncSession): Сессия SQLAlchemy для выполнения запроса.
            to_commit (bool): Флаг, указывающий нужно ли фиксировать изменения в базе данных.

        Returns:
            None
        """
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def create_one(
        self, data: dict, session: AsyncSession, to_commit: bool = True
    ) -> None:
        session.add(self.model(**data))
        if to_commit:
            await session.commit()

    async def get_by_attr(
        self, attribute_name: str, attribute_value: Any, session: AsyncSession
    ) -> model:
        result = await session.execute(
            select(self.model).where(
                getattr(self.model, attribute_name) == attribute_value
            )
        )
        return result.scalars().first()

    async def find_all(self, session: AsyncSession):
        results = await session.execute(select(self.model))
        return results.scalars().all()

    async def delete(
        self, instance: Base, session: AsyncSession, to_commit: bool = True
    ):
        await session.delete(instance)
        if to_commit:
            await session.commit()

    async def add_one(
        self, instance: Base, session: AsyncSession, to_commit: bool = True
    ):
        session.add(instance)
        if to_commit:
            await session.commit()
        await session.refresh(instance)
