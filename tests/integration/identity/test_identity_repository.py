from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from camp_match.modules.identity.adapters.persistence.repository import SqlAlchemyIdentityRepository
from camp_match.modules.identity.application.errors import IdentityAlreadyExists
from camp_match.modules.identity.domain.entities import UserAccount
from camp_match.modules.identity.domain.value_objects import AccountStatus, EmailAddress
from camp_match.shared_kernel.domain.identifiers import EntityId


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_add_and_get(db_session: AsyncSession):
    repo = SqlAlchemyIdentityRepository(db_session)

    account_id = EntityId.new()
    email = EmailAddress("test@example.com")
    account = UserAccount.register(
        id=account_id, email=email, password_hash="hash", created_at=datetime.now(UTC)
    )

    await repo.add(account)
    await db_session.commit()

    # Retrieve by ID
    retrieved_by_id = await repo.get_by_id(account_id)
    assert retrieved_by_id == account

    # Retrieve by email
    retrieved_by_email = await repo.get_by_email(email)
    assert retrieved_by_email == account


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_get_nonexistent(db_session: AsyncSession):
    repo = SqlAlchemyIdentityRepository(db_session)

    assert await repo.get_by_id(EntityId.new()) is None
    assert await repo.get_by_email(EmailAddress("missing@example.com")) is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_add_duplicate_email_raises(db_session: AsyncSession):
    repo = SqlAlchemyIdentityRepository(db_session)
    email = EmailAddress("dup@example.com")

    acc1 = UserAccount.register(
        id=EntityId.new(), email=email, password_hash="hash1", created_at=datetime.now(UTC)
    )
    await repo.add(acc1)
    await db_session.commit()

    acc2 = UserAccount.register(
        id=EntityId.new(), email=email, password_hash="hash2", created_at=datetime.now(UTC)
    )
    with pytest.raises(IdentityAlreadyExists):
        await repo.add(acc2)
        await db_session.commit()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_repository_update_status(db_session: AsyncSession):
    repo = SqlAlchemyIdentityRepository(db_session)
    account_id = EntityId.new()
    account = UserAccount.register(
        id=account_id,
        email=EmailAddress("update@example.com"),
        password_hash="hash",
        created_at=datetime.now(UTC),
    )
    await repo.add(account)
    await db_session.commit()

    account.disable()
    await repo.update(account)
    await db_session.commit()

    retrieved = await repo.get_by_id(account_id)
    assert retrieved is not None
    assert retrieved.status == AccountStatus.DISABLED
