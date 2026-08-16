from datetime import UTC, datetime

from camp_match.modules.identity.domain.entities import UserAccount
from camp_match.modules.identity.domain.value_objects import AccountStatus, EmailAddress
from camp_match.shared_kernel.domain.identifiers import EntityId


def test_user_account_registration():
    user_id = EntityId.new()
    email = EmailAddress("test@example.com")
    now = datetime.now(UTC)

    account = UserAccount.register(
        id=user_id, email=email, password_hash="hashed_password", created_at=now
    )

    assert account.id == user_id
    assert account.email == email
    assert account.status == AccountStatus.ACTIVE
    assert account.can_authenticate is True


def test_user_account_lifecycle():
    account = UserAccount.register(
        id=EntityId.new(),
        email=EmailAddress("test@example.com"),
        password_hash="hash",
        created_at=datetime.now(UTC),
    )

    account.suspend()
    assert account.status == AccountStatus.SUSPENDED
    assert account.can_authenticate is False

    account.reactivate()
    assert account.status == AccountStatus.ACTIVE
    assert account.can_authenticate is True

    account.disable()
    assert account.status == AccountStatus.DISABLED
    assert account.can_authenticate is False

    account.disable()  # harmless no-op
    assert account.status == AccountStatus.DISABLED
