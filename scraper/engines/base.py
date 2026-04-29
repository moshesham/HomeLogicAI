from __future__ import annotations

from abc import ABC, abstractmethod


class BaseScraper(ABC):
    @abstractmethod
    async def scrape(self, url: str) -> dict:
        """Returns raw extracted data dict."""

    @abstractmethod
    def detect(self, url: str) -> bool:
        """Returns True if this engine handles the given URL."""

    @property
    @abstractmethod
    def retailer_name(self) -> str:
        raise NotImplementedError
