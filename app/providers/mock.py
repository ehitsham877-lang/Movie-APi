from __future__ import annotations

from datetime import date

from app.models.api import (
    CreditsResponse,
    KnownForTitle,
    PersonProfile,
    ProviderRef,
    Rating,
    RatingsResponse,
    RecommendationsResponse,
    Review,
    ReviewsResponse,
    TitleDetails,
    TitleSummary,
    TitleType,
    Video,
    VideosResponse,
)
from app.providers.base import Provider


class MockProvider(Provider):
    name = "mock"

    def __init__(self) -> None:
        self._titles: dict[str, TitleDetails] = {
            "tt_mock_1": TitleDetails(
                ref=ProviderRef(provider=self.name, id="tt_mock_1"),
                type=TitleType.movie,
                title="The Example Movie",
                original_title="The Example Movie",
                overview="A sample title used for local development.",
                release_date=date(2020, 1, 1),
                runtime_minutes=110,
                genres=["Drama"],
                poster_url=None,
                backdrop_url=None,
            )
        }

    async def search(self, query: str, title_type: TitleType | None, limit: int) -> list[TitleSummary]:
        query_lower = query.lower().strip()
        results: list[TitleSummary] = []
        for title in self._titles.values():
            if title_type and title.type != title_type:
                continue
            if query_lower in title.title.lower():
                results.append(
                    TitleSummary(
                        ref=title.ref,
                        type=title.type,
                        title=title.title,
                        year=title.release_date.year if title.release_date else None,
                    )
                )
        return results[:limit]

    async def list_titles(self, *, category: str, title_type: TitleType, limit: int, time_window: str | None = None) -> list[TitleSummary]:
        items: list[TitleSummary] = []
        for title in self._titles.values():
            if title.type != title_type:
                continue
            items.append(
                TitleSummary(
                    ref=title.ref,
                    type=title.type,
                    title=title.title,
                    year=title.release_date.year if title.release_date else None,
                    poster_url=title.poster_url,
                )
            )
        return items[:limit]

    async def get_person(self, person_id: str) -> PersonProfile | None:
        if person_id != "nm_mock_1":
            return None
        return PersonProfile(
            ref=ProviderRef(provider=self.name, id=person_id),
            name="Example Actor",
            biography="An example person profile used for local development.",
            profile_url=None,
            known_for=[
                KnownForTitle(
                    ref=ProviderRef(provider=self.name, id="tt_mock_1"),
                    type=TitleType.movie,
                    title="The Example Movie",
                    role="Actor",
                    character="Alex",
                    year=2020,
                    poster_url=None,
                )
            ],
        )

    async def get_recommendations(self, title_id: str, limit: int) -> RecommendationsResponse | None:
        if title_id not in self._titles:
            return None
        return RecommendationsResponse(
            ref=ProviderRef(provider=self.name, id=title_id),
            results=[
                TitleSummary(
                    ref=ProviderRef(provider=self.name, id="tt_mock_1"),
                    type=TitleType.movie,
                    title="The Example Movie",
                    year=2020,
                    poster_url=None,
                )
            ][:limit],
        )

    async def get_reviews(self, title_id: str, limit: int) -> ReviewsResponse | None:
        if title_id not in self._titles:
            return None
        return ReviewsResponse(
            ref=ProviderRef(provider=self.name, id=title_id),
            results=[
                Review(
                    author="MovieCritic99",
                    content="A masterpiece of modern cinema (mock review).",
                    rating=10,
                )
            ][:limit],
        )

    async def get_title(self, title_id: str) -> TitleDetails | None:
        return self._titles.get(title_id)

    async def get_credits(self, title_id: str) -> CreditsResponse | None:
        if title_id not in self._titles:
            return None
        return CreditsResponse(
            ref=ProviderRef(provider=self.name, id=title_id),
            cast=[
                {"id": "nm_mock_1", "name": "Example Actor", "role": "Actor", "character": "Alex"},
                {"id": "nm_mock_2", "name": "Example Actor 2", "role": "Actor", "character": "Sam"},
            ],
            crew=[
                {"id": "nm_mock_3", "name": "Example Director", "role": "Director"},
            ],
        )

    async def get_ratings(self, title_id: str) -> RatingsResponse | None:
        if title_id not in self._titles:
            return None
        return RatingsResponse(
            ref=ProviderRef(provider=self.name, id=title_id),
            ratings=[
                Rating(source="community", value=7.4, votes=1203),
            ],
        )

    async def get_trailers(self, title_id: str) -> VideosResponse | None:
        if title_id not in self._titles:
            return None
        return VideosResponse(
            ref=ProviderRef(provider=self.name, id=title_id),
            videos=[
                Video(
                    site="YouTube",
                    key="dQw4w9WgXcQ",
                    name="Official Trailer",
                    type="Trailer",
                    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                )
            ],
        )
