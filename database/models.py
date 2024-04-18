from sqlalchemy import URL, Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from bot import constants
from core.db import Base


class User(Base):
    telegram_user_id: Mapped[int] = mapped_column(
        Integer, nullable=False, unique=True
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)


class Application(Base):
    url: Mapped[str] = mapped_column(String(constants.MAX_URL_LENGTH), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(constants.MAX_NAME_LENGTH), nullable=False)
    ads_url: Mapped[str] = mapped_column(String(constants.MAX_ADS_URL_LENGTH), nullable=False)
    failure_counter: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self):
        return f"Application {self.name} - url: {self.url}"


class Token(Base):
    token: Mapped[str] = mapped_column(String(constants.MAX_TOKEN_LENGTH), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"{self.token} - is active: {self.is_active}"
