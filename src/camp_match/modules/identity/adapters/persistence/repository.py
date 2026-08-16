"""SQLAlchemy-backed implementation of the IdentityRepository port."""

from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from camp_match.modules.identity.application.errors import IdentityAlreadyExists
from camp_match.modules.identity.adapters.persistence.models import AccountModel
from camp_match.modules.identity.domain.entities import UserAccount
from camp_match.modules.identity.domain.value_objects import AccountStatus, EmailAddress

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from camp_match.shared_kernel.domain.identifiers import EntityId

class SqlAlchemyIdentityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, account: UserAccount) -> None:
        model = AccountModel(
            id=account.id.value,
            email=str(account.email),
            password_hash=account.password_hash,
            status=account.status.name,
            created_at=account.created_at,
            updated_at=account.created_at,
        )
        self._session.add(model)
        try:
            # We flush to trigger the unique constraint check immediately
            await self._session.flush()
        except IntegrityError as e:
            if "identity_accounts_email_key" in str(e):
                raise IdentityAlreadyExists(f"Email {account.email} already exists.") from e
            raise

    async def get_by_email(self, email: EmailAddress) -> UserAccount | None:
        stmt = select(AccountModel).where(AccountModel.email == str(email))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_id(self, identity_id: EntityId) -> UserAccount | None:
        stmt = select(AccountModel).where(AccountModel.id == identity_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update(self, account: UserAccount) -> None:
        stmt = select(AccountModel).where(AccountModel.id == account.id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.status = account.status.name
            # updated_at handled by SQLAlchemy onupdate

    def _to_domain(self, model: AccountModel) -> UserAccount:
        from camp_match.shared_kernel.domain.identifiers import EntityId
        return UserAccount(
            id=EntityId(model.id),
            email=EmailAddress(model.email),
            password_hash=model.password_hash,
            status=AccountStatus[model.status],
            created_at=model.created_at,
        )
