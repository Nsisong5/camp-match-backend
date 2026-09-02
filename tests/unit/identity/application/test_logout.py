import pytest

from camp_match.modules.identity.application.ports.inbound import LogoutRequest
from camp_match.modules.identity.application.use_cases.logout import LogoutUseCase
from tests.support.identity_fakes import FakeAuthenticationSessionPort, FakeUnitOfWork


@pytest.mark.asyncio
@pytest.mark.unit
async def test_logout_idempotency():
    session_port = FakeAuthenticationSessionPort()
    uow = FakeUnitOfWork()
    token = "refresh_00000000-0000-0000-0000-000000000000"

    use_case = LogoutUseCase(session_port, uow)
    request = LogoutRequest(refresh_token=token)

    # First call
    await use_case.execute(request)
    assert token in session_port.revoked_tokens
    assert uow.committed

    # Second call - should not raise
    await use_case.execute(request)
    assert token in session_port.revoked_tokens
    assert uow.committed
