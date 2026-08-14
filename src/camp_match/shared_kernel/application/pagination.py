from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PageRequest:
    page: int = 1
    page_size: int = 20

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if not (1 <= self.page_size <= 100):
            raise ValueError("page_size must be between 1 and 100")


@dataclass(frozen=True)
class Page[T]:
    items: list[T]
    total: int
    page: int
    page_size: int
