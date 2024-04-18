from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Application
from repositories import ApplicationRepository, TokenRepository, UserRepository
from utils.repository import AbstractRepository

from bot import constants

class UserService:
    def __init__(self, user_repo: AbstractRepository):
        self.user_repo: AbstractRepository = user_repo()

    async def create_user(
        self, data: dict, session: AsyncSession, to_commit: bool = True
    ) -> None:
        return await self.user_repo.create_one(data, session, to_commit)

    async def get_user_by_attr(
        self, attr_name: str, attr_value: Any, session: AsyncSession
    ):
        return await self.user_repo.get_by_attr(attr_name, attr_value, session)

    async def get_all_users(self, session):
        return await self.user_repo.find_all(session)

    async def is_admin(self, user_id: int, session):
        user = await self.get_user_by_attr(
            "telegram_user_id", user_id, session
        )
        return user.is_admin


class TokenServices:
    def __init__(self, token_repo: AbstractRepository):
        self.token_repo: AbstractRepository = token_repo()

    async def create_token(
        self, data: dict, session: AsyncSession, to_commit: bool = True
    ) -> None:
        return await self.token_repo.create_one(data, session, to_commit)

    async def get_token_by_attr(
        self, attr_name: str, attr_value: Any, session: AsyncSession
    ):
        return await self.token_repo.get_by_attr(
            attr_name, attr_value, session
        )

    async def check_user_token(self, token: str, session: AsyncSession):
        token = await self.get_token_by_attr("token", token, session)
        if token is None:
            raise ValueError(
            constants.INCORRECT_TOKEN
            )
        elif token.is_active:
            token.is_active = False
            await self.token_repo.add_one(token, session, to_commit=True)
        else:
            raise ValueError(
                constants.TOKEN_IS_INACTIVE
            )

    async def check_generated_token(self, token: str, session: AsyncSession):
        if len(token) > constants.MAX_TOKEN_LENGTH:
            raise ValueError(constants.TOKEN_LENGTH)
        if await self.get_token_by_attr("token", token, session):
            raise ValueError(constants.TOKEN_EXISTS)
        else:
            await self.create_token({"token": token}, session)


class ApplicationServices:
    def __init__(self, application_repo: AbstractRepository):
        self.application_repo: AbstractRepository = application_repo()

    async def create_application(
        self, data: dict, session: AsyncSession, to_commit: bool = True
    ) -> None:
        if len(data["name"]) > constants.MAX_NAME_LENGTH:
            raise ValueError(constants.NAME_LENGTH_MESSAGE)
        if len(data["url"]) > constants.MAX_URL_LENGTH or len(data["ads_url"]) > constants.MAX_URL_LENGTH:
            raise ValueError(constants.URL_LENGTH_MESSAGE.format(constants.MAX_URL_LENGTH))
        return await self.application_repo.create_one(data, session, to_commit)

    async def get_application_by_attr(
        self, attr_name: str, attr_value: Any, session: AsyncSession
    ):
        return await self.application_repo.get_by_attr(
            attr_name, attr_value, session
        )

    async def get_all_applications(self, session: AsyncSession):
        return await self.application_repo.find_all(session)

    async def increment_failure_counter(
        self,
        application: Application,
        session: AsyncSession,
        to_commit: bool = True,
    ):
        application.failure_counter += 1
        await self.application_repo.add_one(application, session, to_commit)

    async def reset_failure_counter(
        self,
        application: Application,
        session: AsyncSession,
        to_commit: bool = True,
    ):
        application.failure_counter = 0
        await self.application_repo.add_one(application, session, to_commit)

    async def delete(self, instance: Application, session: AsyncSession):
        await self.application_repo.delete(instance, session)


user_service = UserService(UserRepository)
token_service = TokenServices(TokenRepository)
application_service = ApplicationServices(ApplicationRepository)
