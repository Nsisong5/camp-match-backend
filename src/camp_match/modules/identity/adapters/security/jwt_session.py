import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import jwt
import structlog
from sqlalchemy import select

from camp_match.config.settings import Settings
from camp_match.modules.identity.adapters.persistence.models import RefreshTokenModel
from camp_match.modules.identity.application.errors import InvalidCredentials
from camp_match.modules.identity.application.ports.outbound import TokenPair
from camp_match.shared_kernel.domain.identifiers import EntityId

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


class JwtAuthenticationSessionAdapter:
    def __init__(self, session: "AsyncSession", settings: Settings) -> None:
        self._session = session
        self._settings = settings

    async def issue_tokens(self, identity_id: EntityId) -> TokenPair:
        now = datetime.now(UTC)
        access_token = self._create_access_token(identity_id, now)

        refresh_token, token_model = await self._create_refresh_token(identity_id, now)
        self._session.add(token_model)
        await self._session.flush()

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self._settings.jwt_access_token_expire_minutes * 60,
        )

    async def refresh(self, refresh_token: str) -> TokenPair:
        refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token_hash == refresh_token_hash)
        result = await self._session.execute(stmt)
        token_model = result.scalar_one_or_none()

        now = datetime.now(UTC)

        if not token_model:
            logger.warning("refresh_token_unknown", token_hash=refresh_token_hash)
            raise InvalidCredentials("Invalid credentials.")

        if token_model.revoked_at:
            logger.warning(
                "refresh_token_reused",
                token_hash=refresh_token_hash,
                account_id=str(token_model.account_id),
            )
            raise InvalidCredentials("Invalid credentials.") from None

        if token_model.expires_at < now:
            logger.warning(
                "refresh_token_expired",
                token_hash=refresh_token_hash,
                account_id=str(token_model.account_id),
            )
            raise InvalidCredentials("Invalid credentials.") from None

        # Revoke old token
        token_model.revoked_at = now

        # Issue new tokens
        identity_id = EntityId(token_model.account_id)
        access_token = self._create_access_token(identity_id, now)
        new_refresh_token, new_token_model = await self._create_refresh_token(identity_id, now)
        
        # Link rotation
        token_model.replaced_by_id = new_token_model.id
        
        self._session.add(new_token_model)
        await self._session.flush()

        return TokenPair(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=self._settings.jwt_access_token_expire_minutes * 60,
        )

    async def revoke(self, refresh_token: str) -> None:
        refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token_hash == refresh_token_hash)
        result = await self._session.execute(stmt)
        token_model = result.scalar_one_or_none()

        if token_model and not token_model.revoked_at:
            token_model.revoked_at = datetime.now(UTC)
            logger.info("refresh_token_revoked", token_hash=refresh_token_hash)
        else:
            logger.info("refresh_token_revocation_noop", token_hash=refresh_token_hash)

    async def decode_access_token(self, access_token: str) -> EntityId:
        try:
            payload = jwt.decode(
                access_token, self._settings.jwt_secret_key, algorithms=["HS256"]
            )
            if payload.get("type") != "access":
                logger.warning("access_token_invalid_type", type=payload.get("type"))
                raise InvalidCredentials("Invalid credentials.")
            
            return EntityId.from_string(payload["sub"])
        except jwt.ExpiredSignatureError as e:
            logger.warning("access_token_expired")
            raise InvalidCredentials("Invalid credentials.") from e
        except jwt.PyJWTError as e:
            logger.warning("access_token_invalid", error=str(e))
            raise InvalidCredentials("Invalid credentials.") from e

    def _create_access_token(self, identity_id: EntityId, issued_at: datetime) -> str:
        payload = {
            "sub": str(identity_id),
            "iat": issued_at,
            "exp": issued_at + timedelta(minutes=self._settings.jwt_access_token_expire_minutes),
            "type": "access",
        }
        return jwt.encode(payload, self._settings.jwt_secret_key, algorithm="HS256")

    async def _create_refresh_token(self, identity_id: EntityId, issued_at: datetime) -> tuple[str, RefreshTokenModel]:
        refresh_token = secrets.token_urlsafe(48)
        refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        expires_at = issued_at + timedelta(days=self._settings.refresh_token_expire_days)

        token_model = RefreshTokenModel(
            id=EntityId.new().value,
            account_id=identity_id.value,
            token_hash=refresh_token_hash,
            issued_at=issued_at,
            expires_at=expires_at,
        )
        return refresh_token, token_model
