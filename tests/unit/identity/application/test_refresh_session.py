import pytest

from camp_match.modules.identity.application.ports.inbound import RefreshRequest
from camp_match.modules.identity.application.use_cases.refresh_session import RefreshSessionUseCase
from tests.support.identity_fakes import FakeAuthenticationSessionPort


@pytest.mark.asyncio
@pytest.mark.unit
async def test_refresh_session_success():
    session_port = FakeAuthenticationSessionPort()
    # "refresh_..." is our fake format
    token = "refresh_00000000-0000-0000-0000-000000000000"

    use_case = RefreshSessionUseCase(session_port)
    request = RefreshRequest(refresh_token=token)

    response = await use_case.execute(request)

    assert response.access_token.startswith("access_")
    assert response.refresh_token.startswith("refresh_")
