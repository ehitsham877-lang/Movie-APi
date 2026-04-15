from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.api import (
    CreditsResponse,
    PersonProfile,
    RatingsResponse,
    RecommendationsResponse,
    ReviewsResponse,
    TitleDetails,
    TitleSummary,
    TitleType,
    VideosResponse,
)


class Provider(ABC):
    name: str

    async def aclose(self) -> None:
        return None

    async def list_titles(self, *, category: str, title_type: TitleType, limit: int, time_window: str | None = None) -> list[TitleSummary]:
        raise NotImplementedError

    @abstractmethod
    async def search(self, query: str, title_type: TitleType | None, limit: int) -> list[TitleSummary]:
        raise NotImplementedError

    async def get_person(self, person_id: str) -> PersonProfile | None:
        raise NotImplementedError

    async def get_recommendations(self, title_id: str, limit: int) -> RecommendationsResponse | None:
        raise NotImplementedError

    async def get_reviews(self, title_id: str, limit: int) -> ReviewsResponse | None:
        raise NotImplementedError

    @abstractmethod
    async def get_title(self, title_id: str) -> TitleDetails | None:
        raise NotImplementedError

    @abstractmethod
    async def get_credits(self, title_id: str) -> CreditsResponse | None:
        raise NotImplementedError

    @abstractmethod
    async def get_ratings(self, title_id: str) -> RatingsResponse | None:
        raise NotImplementedError

    @abstractmethod
    async def get_trailers(self, title_id: str) -> VideosResponse | None:
        raise NotImplementedError
