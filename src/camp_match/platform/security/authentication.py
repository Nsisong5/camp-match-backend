from typing import Annotated

from fastapi import Depends, Header, HTTPException

from camp_match.modules.identity.adapters.api.dependencies import get_auth_session
from camp_match.modules.identity.adapters.security.jwt_session import (
    JwtAuthenticationSessionAdapter,
)
from camp_match.shared_kernel.domain.identifiers import EntityId


async def get_current_identity_id(
    authorization: Annotated[str | None, Header()] = None,
    auth: Annotated[JwtAuthenticationSessionAdapter, Depends(get_auth_session)] = ...,  # type: ignore
) -> EntityId:
    print("\n" + "="*60)
    print(f"[DEBUG AUTH] Incoming request authorization header: {repr(authorization)}")
    print(f"[DEBUG AUTH] Required backend format: 'Authorization: Bearer <your_jwt_token>'")
    print(f"[DEBUG AUTH] Validation checks: Present? {bool(authorization)}, Starts with 'Bearer '? {authorization.startswith('Bearer ') if authorization else False}")
    print("="*60 + "\n")

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]
    return await auth.decode_access_token(token)
