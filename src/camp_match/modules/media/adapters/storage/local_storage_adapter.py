from __future__ import annotations

from pathlib import Path
from camp_match.modules.media.application.ports.outbound import AccessGrant, StoragePort
from camp_match.modules.media.adapters.storage.access_token import issue_token


class LocalFileSystemStorageAdapter(StoragePort):
    def __init__(self, storage_path: str, secret: str, ttl_seconds: int = 300) -> None:
        self._storage_path = Path(storage_path)
        self._secret = secret
        self._ttl_seconds = ttl_seconds

    def store(self, key: str, data: bytes, content_type: str) -> None:
        file_path = self._storage_path / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)

    def delete(self, key: str) -> None:
        file_path = self._storage_path / key
        if file_path.exists():
            file_path.unlink()

    def exists(self, key: str) -> bool:
        file_path = self._storage_path / key
        return file_path.exists()

    def issue_access_token(self, key: str) -> AccessGrant:
        return issue_token(key, self._secret, self._ttl_seconds)
