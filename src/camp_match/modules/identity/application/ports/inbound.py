"""Inbound ports for the Identity module defining use case interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class RegistrationRequest:
    email: str
    raw_password: str


@dataclass(frozen=True)
class RegistrationResponse:
    id: str
    email: str
    status: str
    created_at: datetime


@dataclass(frozen=True)
class AuthenticationRequest:
    email: str
    raw_password: str


@dataclass(frozen=True)
class TokenResponse:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


@dataclass(frozen=True)
class RefreshRequest:
    refresh_token: str


@dataclass(frozen=True)
class LogoutRequest:
    refresh_token: str


@dataclass(frozen=True)
class IdentityQueryRequest:
    identity_id: str


@dataclass(frozen=True)
class IdentityResponse:
    id: str
    email: str
    status: str
    created_at: datetime


@dataclass(frozen=True)
class UpdateStatusRequest:
    identity_id: str


class RegisterAccount(Protocol):
    async def execute(self, request: RegistrationRequest) -> RegistrationResponse:
        """Register a new user account."""
        ...


class AuthenticateUser(Protocol):
    async def execute(self, request: AuthenticationRequest) -> TokenResponse:
        """Authenticate a user and return a token pair."""
        ...


class RefreshSession(Protocol):
    async def execute(self, request: RefreshRequest) -> TokenResponse:
        """Refresh an existing authentication session."""
        ...


class Logout(Protocol):
    async def execute(self, request: LogoutRequest) -> None:
        """Revoke the current authentication session."""
        ...


class GetIdentityById(Protocol):
    async def execute(self, request: IdentityQueryRequest) -> IdentityResponse:
        """Retrieve identity details by ID."""
        ...


class DisableAccount(Protocol):
    async def execute(self, request: UpdateStatusRequest) -> IdentityResponse:
        """Disable a user account."""
        ...


class ReactivateAccount(Protocol):
    async def execute(self, request: UpdateStatusRequest) -> IdentityResponse:
        """Reactivate a disabled user account."""
        ...
