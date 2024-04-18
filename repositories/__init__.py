from database.models import Application, Token, User
from utils.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User


class ApplicationRepository(SQLAlchemyRepository):
    model = Application


class TokenRepository(SQLAlchemyRepository):
    model = Token
