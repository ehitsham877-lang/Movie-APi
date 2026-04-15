from __future__ import annotations

from datetime import datetime
from datetime import date

import httpx

from app.core.config import settings
from app.models.api import (
    CreditsResponse,
    KnownForTitle,
    Person,
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


class TMDbProvider(Provider):
    name = "tmdb"

    def __init__(self) -> None:
        if not settings.tmdb_api_key:
            raise ValueError("TMDB_API_KEY is required to use tmdb provider")
        self._client = httpx.AsyncClient(base_url=settings.tmdb_base_url, timeout=20.0)

    async def aclose(self) -> None:
        await self._client.aclose()

    def _img(self, path: str | None, size: str = "w500") -> str | None:
        if not path:
            return None
        return f"{settings.tmdb_image_base_url.rstrip('/')}/{size}{path}"

    def _parse_dt(self, s: str | None) -> datetime | None:
        if not s:
            return None
        try:
            # TMDb typically returns ISO-8601 with trailing Z.
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None

    async def _get(self, path: str, *, params: dict | None = None) -> dict:
        base_params = {"api_key": settings.tmdb_api_key, "language": "en-US"}
        if params:
            base_params.update(params)
        resp = await self._client.get(path, params=base_params)
        resp.raise_for_status()
        return resp.json()

    async def list_titles(
        self,
        *,
        category: str,
        title_type: TitleType,
        limit: int,
        time_window: str | None = None,
    ) -> list[TitleSummary]:
        if title_type == TitleType.movie:
            path = {
                "popular": "/movie/popular",
                "top_rated": "/movie/top_rated",
                "now_playing": "/movie/now_playing",
                "upcoming": "/movie/upcoming",
                "trending": f"/trending/movie/{time_window or 'day'}",
            }.get(category)
            if not path:
                raise ValueError("Unknown movie category")
            payload = await self._get(path, params={"page": 1})
            return [self._movie_summary(i) for i in payload.get("results", [])][:limit]

        path = {
            "popular": "/tv/popular",
            "top_rated": "/tv/top_rated",
            "on_the_air": "/tv/on_the_air",
            "airing_today": "/tv/airing_today",
            "trending": f"/trending/tv/{time_window or 'day'}",
        }.get(category)
        if not path:
            raise ValueError("Unknown tv category")
        payload = await self._get(path, params={"page": 1})
        return [self._tv_summary(i) for i in payload.get("results", [])][:limit]

    def _encode_id(self, title_type: TitleType, numeric_id: int | str) -> str:
        return f"{title_type.value}:{numeric_id}"

    def _decode_id(self, title_id: str) -> tuple[TitleType, str]:
        if ":" not in title_id:
            raise ValueError("TMDb title_id must be in 'movie:<id>' or 'tv:<id>' format")
        kind, numeric_id = title_id.split(":", 1)
        if kind not in (TitleType.movie.value, TitleType.tv.value):
            raise ValueError("TMDb title_id must be in 'movie:<id>' or 'tv:<id>' format")
        return TitleType(kind), numeric_id

    def _parse_year(self, s: str | None) -> int | None:
        if not s:
            return None
        try:
            return int(s.split("-", 1)[0])
        except Exception:
            return None

    def _parse_date(self, s: str | None) -> date | None:
        if not s:
            return None
        try:
            y, m, d = s.split("-")
            return date(int(y), int(m), int(d))
        except Exception:
            return None

    async def search(self, query: str, title_type: TitleType | None, limit: int) -> list[TitleSummary]:
        if title_type == TitleType.movie:
            payload = await self._get("/search/movie", params={"query": query, "page": 1, "include_adult": False})
            items = payload.get("results", [])
            return [self._movie_summary(i) for i in items][:limit]
        if title_type == TitleType.tv:
            payload = await self._get("/search/tv", params={"query": query, "page": 1})
            items = payload.get("results", [])
            return [self._tv_summary(i) for i in items][:limit]

        payload = await self._get("/search/multi", params={"query": query, "page": 1, "include_adult": False})
        results: list[TitleSummary] = []
        for item in payload.get("results", []):
            media_type = item.get("media_type")
            if media_type == "movie":
                results.append(self._movie_summary(item))
            elif media_type == "tv":
                results.append(self._tv_summary(item))
        return results[:limit]

    def _movie_summary(self, item: dict) -> TitleSummary:
        numeric_id = item.get("id")
        return TitleSummary(
            ref=ProviderRef(provider=self.name, id=self._encode_id(TitleType.movie, numeric_id)),
            type=TitleType.movie,
            title=item.get("title") or item.get("original_title") or "",
            year=self._parse_year(item.get("release_date")),
            poster_url=self._img(item.get("poster_path")),
        )

    def _tv_summary(self, item: dict) -> TitleSummary:
        numeric_id = item.get("id")
        return TitleSummary(
            ref=ProviderRef(provider=self.name, id=self._encode_id(TitleType.tv, numeric_id)),
            type=TitleType.tv,
            title=item.get("name") or item.get("original_name") or "",
            year=self._parse_year(item.get("first_air_date")),
            poster_url=self._img(item.get("poster_path")),
        )

    async def get_title(self, title_id: str) -> TitleDetails | None:
        title_type, numeric_id = self._decode_id(title_id)
        if title_type == TitleType.movie:
            item = await self._get(f"/movie/{numeric_id}")
            return TitleDetails(
                ref=ProviderRef(provider=self.name, id=title_id),
                type=TitleType.movie,
                title=item.get("title") or item.get("original_title") or "",
                original_title=item.get("original_title"),
                overview=item.get("overview"),
                release_date=self._parse_date(item.get("release_date")),
                runtime_minutes=item.get("runtime"),
                genres=[g.get("name") for g in item.get("genres", []) if g.get("name")],
                poster_url=self._img(item.get("poster_path")),
                backdrop_url=self._img(item.get("backdrop_path"), size="w780"),
            )

        item = await self._get(f"/tv/{numeric_id}")
        episode_runtime = None
        runtimes = item.get("episode_run_time") or []
        if runtimes:
            episode_runtime = runtimes[0]
        return TitleDetails(
            ref=ProviderRef(provider=self.name, id=title_id),
            type=TitleType.tv,
            title=item.get("name") or item.get("original_name") or "",
            original_title=item.get("original_name"),
            overview=item.get("overview"),
            release_date=self._parse_date(item.get("first_air_date")),
            runtime_minutes=episode_runtime,
            genres=[g.get("name") for g in item.get("genres", []) if g.get("name")],
            poster_url=self._img(item.get("poster_path")),
            backdrop_url=self._img(item.get("backdrop_path"), size="w780"),
        )

    async def get_person(self, person_id: str) -> PersonProfile | None:
        item = await self._get(f"/person/{person_id}")
        credits = await self._get(f"/person/{person_id}/combined_credits", params={"language": "en-US"})

        known_for: list[KnownForTitle] = []
        cast_items = credits.get("cast", []) or []
        crew_items = credits.get("crew", []) or []

        # Prefer cast items by popularity; fall back to crew.
        cast_items_sorted = sorted(cast_items, key=lambda x: (x.get("popularity") or 0), reverse=True)
        crew_items_sorted = sorted(crew_items, key=lambda x: (x.get("popularity") or 0), reverse=True)

        for c in cast_items_sorted[:30]:
            media_type = c.get("media_type")
            if media_type not in ("movie", "tv"):
                continue
            ttype = TitleType.movie if media_type == "movie" else TitleType.tv
            numeric_id = c.get("id")
            title = c.get("title") or c.get("name") or c.get("original_title") or c.get("original_name") or ""
            known_for.append(
                KnownForTitle(
                    ref=ProviderRef(provider=self.name, id=self._encode_id(ttype, numeric_id)),
                    type=ttype,
                    title=title,
                    role="Actor",
                    character=c.get("character"),
                    year=self._parse_year(c.get("release_date") or c.get("first_air_date")),
                    poster_url=self._img(c.get("poster_path")),
                )
            )

        if not known_for:
            for c in crew_items_sorted[:30]:
                media_type = c.get("media_type")
                if media_type not in ("movie", "tv"):
                    continue
                ttype = TitleType.movie if media_type == "movie" else TitleType.tv
                numeric_id = c.get("id")
                title = c.get("title") or c.get("name") or c.get("original_title") or c.get("original_name") or ""
                known_for.append(
                    KnownForTitle(
                        ref=ProviderRef(provider=self.name, id=self._encode_id(ttype, numeric_id)),
                        type=ttype,
                        title=title,
                        role=c.get("job"),
                        year=self._parse_year(c.get("release_date") or c.get("first_air_date")),
                        poster_url=self._img(c.get("poster_path")),
                    )
                )

        return PersonProfile(
            ref=ProviderRef(provider=self.name, id=str(person_id)),
            name=item.get("name") or "",
            biography=item.get("biography"),
            birthday=self._parse_date(item.get("birthday")),
            profile_url=self._img(item.get("profile_path")),
            known_for=known_for[:20],
        )

    async def get_credits(self, title_id: str) -> CreditsResponse | None:
        title_type, numeric_id = self._decode_id(title_id)
        path = f"/movie/{numeric_id}/credits" if title_type == TitleType.movie else f"/tv/{numeric_id}/credits"
        payload = await self._get(path)

        cast = [
            Person(
                id=str(p.get("id")),
                name=p.get("name") or "",
                role="Actor",
                character=p.get("character"),
            )
            for p in payload.get("cast", [])[:50]
        ]
        crew = [
            Person(
                id=str(p.get("id")),
                name=p.get("name") or "",
                role=p.get("job"),
            )
            for p in payload.get("crew", [])[:50]
        ]
        return CreditsResponse(ref=ProviderRef(provider=self.name, id=title_id), cast=cast, crew=crew)

    async def get_ratings(self, title_id: str) -> RatingsResponse | None:
        title_type, numeric_id = self._decode_id(title_id)
        item = await self._get(f"/movie/{numeric_id}") if title_type == TitleType.movie else await self._get(f"/tv/{numeric_id}")
        value = item.get("vote_average")
        votes = item.get("vote_count")
        ratings: list[Rating] = []
        if value is not None:
            try:
                ratings.append(Rating(source="tmdb", value=float(value), votes=int(votes) if votes is not None else None))
            except Exception:
                pass
        return RatingsResponse(ref=ProviderRef(provider=self.name, id=title_id), ratings=ratings)

    async def get_trailers(self, title_id: str) -> VideosResponse | None:
        title_type, numeric_id = self._decode_id(title_id)
        path = f"/movie/{numeric_id}/videos" if title_type == TitleType.movie else f"/tv/{numeric_id}/videos"
        payload = await self._get(path)

        videos: list[Video] = []
        for v in payload.get("results", []):
            site = v.get("site")
            key = v.get("key")
            if not site or not key:
                continue
            url = None
            if site.lower() == "youtube":
                url = f"https://www.youtube.com/watch?v={key}"
            videos.append(
                Video(
                    site=site,
                    key=key,
                    name=v.get("name"),
                    type=v.get("type"),
                    url=url,
                )
            )

        return VideosResponse(ref=ProviderRef(provider=self.name, id=title_id), videos=videos)

    async def get_recommendations(self, title_id: str, limit: int) -> RecommendationsResponse | None:
        title_type, numeric_id = self._decode_id(title_id)
        path = f"/movie/{numeric_id}/recommendations" if title_type == TitleType.movie else f"/tv/{numeric_id}/recommendations"
        payload = await self._get(path, params={"page": 1})
        items = payload.get("results", []) or []
        results: list[TitleSummary] = []
        if title_type == TitleType.movie:
            results = [self._movie_summary(i) for i in items][:limit]
        else:
            results = [self._tv_summary(i) for i in items][:limit]
        return RecommendationsResponse(ref=ProviderRef(provider=self.name, id=title_id), results=results)

    async def get_reviews(self, title_id: str, limit: int) -> ReviewsResponse | None:
        title_type, numeric_id = self._decode_id(title_id)
        path = f"/movie/{numeric_id}/reviews" if title_type == TitleType.movie else f"/tv/{numeric_id}/reviews"
        payload = await self._get(path, params={"page": 1})
        out: list[Review] = []
        for r in (payload.get("results", []) or [])[:limit]:
            author = r.get("author") or ""
            content = r.get("content") or ""
            author_details = r.get("author_details") or {}
            rating_val = author_details.get("rating")
            rating: float | None = None
            if rating_val is not None:
                try:
                    rating = float(rating_val)
                except Exception:
                    rating = None
            out.append(
                Review(
                    author=author,
                    content=content,
                    rating=rating,
                    created_at=self._parse_dt(r.get("created_at")),
                    url=r.get("url"),
                )
            )
        return ReviewsResponse(ref=ProviderRef(provider=self.name, id=title_id), results=out)
