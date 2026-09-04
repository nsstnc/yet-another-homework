import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
from passlib.context import CryptContext
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Security:
    @staticmethod
    def hash(password: str):
        return pwd_context.hash(password)

    @staticmethod
    def verify(password: str, hashed_password: str):
        return pwd_context.verify(password, hashed_password)

    @staticmethod
    def generate_refresh_token() -> str:
        return secrets.token_urlsafe(48)

    @staticmethod
    def hash_refresh_token(refresh_token):
        return hashlib.sha256(
            refresh_token.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def generate_access_token(
            user_id: str,
            session_id: str,
    ) -> str:
        now = datetime.now(UTC)

        payload = {
            "sub": user_id,
            "sid": session_id,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

    @staticmethod
    def decode_access_token(token: str) -> dict:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "access":
            raise JWTError("Invalid token type")

        return payload


@dataclass
class Tokens:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
