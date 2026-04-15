from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings
from app.providers.base import Provider
from app.providers.mock import MockProvider
from app.providers.tmdb import TMDbProvider


@dataclass(frozen=True)
class ProviderRegistry:
    _providers: dict[str, Provider]

    def get(self, name: str) -> Provider | None:
        return self._providers.get(name)

    def providers(self) -> list[Provider]:
        return list(self._providers.values())

    def list_provider_names(self) -> list[str]:
        return list(self._providers.keys())


def _build_registry() -> ProviderRegistry:
    provider_names = [p.strip() for p in settings.providers.split(",") if p.strip()]
    providers: dict[str, Provider] = {}

    for name in provider_names:
        if name == "mock":
            providers[name] = MockProvider()
            continue
        if name == "tmdb":
            if settings.tmdb_api_key:
                providers[name] = TMDbProvider()
            continue
        # Unknown providers are ignored so the app still boots.

    if not providers:
        providers["mock"] = MockProvider()

    return ProviderRegistry(_providers=providers)


registry = _build_registry()
