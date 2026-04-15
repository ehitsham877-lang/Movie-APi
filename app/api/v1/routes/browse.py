from fastapi import APIRouter, HTTPException, Query

from app.models.api import SearchResponse, TitleType
from app.services.registry import registry

router = APIRouter()


def _normalize_provider(provider: str | None) -> str | None:
    if provider is None:
        return None
    cleaned = provider.strip()
    if not cleaned:
        return None
    if cleaned.lower() in {"none", "null"}:
        return None
    if cleaned in {"{}", "[]"}:
        return None
    if cleaned.startswith("{") and cleaned.endswith("}"):
        return None
    return cleaned


def _pick_provider(provider: str | None) -> str:
    provider = _normalize_provider(provider)
    if provider:
        return provider
    if registry.get("tmdb"):
        return "tmdb"
    names = registry.list_provider_names()
    return names[0] if names else "mock"


@router.get("/movies/trending", response_model=SearchResponse)
async def movies_trending(
    provider: str | None = Query(default=None),
    time_window: str = Query(default="day", pattern="^(day|week)$"),
    limit: int = Query(default=20, ge=1, le=50),
) -> SearchResponse:
    provider_obj = registry.get(_pick_provider(provider))
    if not provider_obj:
        raise HTTPException(status_code=404, detail="Unknown provider")
    try:
        results = await provider_obj.list_titles(category="trending", title_type=TitleType.movie, limit=limit, time_window=time_window)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return SearchResponse(results=results)


@router.get("/movies/popular", response_model=SearchResponse)
async def movies_popular(
    provider: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
) -> SearchResponse:
    provider_obj = registry.get(_pick_provider(provider))
    if not provider_obj:
        raise HTTPException(status_code=404, detail="Unknown provider")
    results = await provider_obj.list_titles(category="popular", title_type=TitleType.movie, limit=limit)
    return SearchResponse(results=results)


@router.get("/movies/top-rated", response_model=SearchResponse)
async def movies_top_rated(
    provider: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
) -> SearchResponse:
    provider_obj = registry.get(_pick_provider(provider))
    if not provider_obj:
        raise HTTPException(status_code=404, detail="Unknown provider")
    results = await provider_obj.list_titles(category="top_rated", title_type=TitleType.movie, limit=limit)
    return SearchResponse(results=results)


@router.get("/movies/now-playing", response_model=SearchResponse)
async def movies_now_playing(
    provider: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
) -> SearchResponse:
    provider_obj = registry.get(_pick_provider(provider))
    if not provider_obj:
        raise HTTPException(status_code=404, detail="Unknown provider")
    results = await provider_obj.list_titles(category="now_playing", title_type=TitleType.movie, limit=limit)
    return SearchResponse(results=results)


@router.get("/movies/upcoming", response_model=SearchResponse)
async def movies_upcoming(
    provider: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
) -> SearchResponse:
    provider_obj = registry.get(_pick_provider(provider))
    if not provider_obj:
        raise HTTPException(status_code=404, detail="Unknown provider")
    results = await provider_obj.list_titles(category="upcoming", title_type=TitleType.movie, limit=limit)
    return SearchResponse(results=results)


@router.get("/tv/trending", response_model=SearchResponse)
async def tv_trending(
    provider: str | None = Query(default=None),
    time_window: str = Query(default="day", pattern="^(day|week)$"),
    limit: int = Query(default=20, ge=1, le=50),
) -> SearchResponse:
    provider_obj = registry.get(_pick_provider(provider))
    if not provider_obj:
        raise HTTPException(status_code=404, detail="Unknown provider")
    try:
        results = await provider_obj.list_titles(category="trending", title_type=TitleType.tv, limit=limit, time_window=time_window)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return SearchResponse(results=results)


@router.get("/tv/popular", response_model=SearchResponse)
async def tv_popular(
    provider: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
) -> SearchResponse:
    provider_obj = registry.get(_pick_provider(provider))
    if not provider_obj:
        raise HTTPException(status_code=404, detail="Unknown provider")
    results = await provider_obj.list_titles(category="popular", title_type=TitleType.tv, limit=limit)
    return SearchResponse(results=results)


@router.get("/tv/top-rated", response_model=SearchResponse)
async def tv_top_rated(
    provider: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
) -> SearchResponse:
    provider_obj = registry.get(_pick_provider(provider))
    if not provider_obj:
        raise HTTPException(status_code=404, detail="Unknown provider")
    results = await provider_obj.list_titles(category="top_rated", title_type=TitleType.tv, limit=limit)
    return SearchResponse(results=results)


@router.get("/tv/on-the-air", response_model=SearchResponse)
async def tv_on_the_air(
    provider: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
) -> SearchResponse:
    provider_obj = registry.get(_pick_provider(provider))
    if not provider_obj:
        raise HTTPException(status_code=404, detail="Unknown provider")
    results = await provider_obj.list_titles(category="on_the_air", title_type=TitleType.tv, limit=limit)
    return SearchResponse(results=results)


@router.get("/tv/airing-today", response_model=SearchResponse)
async def tv_airing_today(
    provider: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
) -> SearchResponse:
    provider_obj = registry.get(_pick_provider(provider))
    if not provider_obj:
        raise HTTPException(status_code=404, detail="Unknown provider")
    results = await provider_obj.list_titles(category="airing_today", title_type=TitleType.tv, limit=limit)
    return SearchResponse(results=results)
