from fastapi import APIRouter, HTTPException

from fastapi import Query

from app.models.api import (
    CreditsResponse,
    RatingsResponse,
    RecommendationsResponse,
    ReviewsResponse,
    TitleDetails,
    TitleFullResponse,
    VideosResponse,
)
from app.services.registry import registry

router = APIRouter(prefix="/titles")


def _parse_ref(ref: str) -> tuple[str, str]:
    if ":" not in ref:
        raise ValueError("Title reference must be in 'provider:id' format")
    provider, title_id = ref.split(":", 1)
    return provider, title_id


@router.get("/{ref}", response_model=TitleDetails)
async def get_title(ref: str) -> TitleDetails:
    try:
        provider_name, title_id = _parse_ref(ref)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    provider = registry.get(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Unknown provider")
    title = await provider.get_title(title_id=title_id)
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")
    return title


@router.get("/{ref}/credits", response_model=CreditsResponse)
async def get_credits(ref: str) -> CreditsResponse:
    try:
        provider_name, title_id = _parse_ref(ref)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    provider = registry.get(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Unknown provider")
    credits = await provider.get_credits(title_id=title_id)
    if not credits:
        raise HTTPException(status_code=404, detail="Credits not found")
    return credits


@router.get("/{ref}/ratings", response_model=RatingsResponse)
async def get_ratings(ref: str) -> RatingsResponse:
    try:
        provider_name, title_id = _parse_ref(ref)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    provider = registry.get(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Unknown provider")
    ratings = await provider.get_ratings(title_id=title_id)
    if not ratings:
        raise HTTPException(status_code=404, detail="Ratings not found")
    return ratings


@router.get("/{ref}/trailers", response_model=VideosResponse)
async def get_trailers(ref: str) -> VideosResponse:
    try:
        provider_name, title_id = _parse_ref(ref)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    provider = registry.get(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Unknown provider")
    videos = await provider.get_trailers(title_id=title_id)
    if not videos:
        raise HTTPException(status_code=404, detail="Trailers not found")
    return videos


@router.get("/{ref}/full", response_model=TitleFullResponse)
async def get_full(ref: str) -> TitleFullResponse:
    try:
        provider_name, title_id = _parse_ref(ref)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    provider = registry.get(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Unknown provider")

    title = await provider.get_title(title_id=title_id)
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")

    credits = await provider.get_credits(title_id=title_id)
    ratings = await provider.get_ratings(title_id=title_id)
    trailers = await provider.get_trailers(title_id=title_id)
    return TitleFullResponse(title=title, credits=credits, ratings=ratings, trailers=trailers)


@router.get("/{ref}/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    ref: str,
    limit: int = Query(default=20, ge=1, le=50),
) -> RecommendationsResponse:
    try:
        provider_name, title_id = _parse_ref(ref)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    provider = registry.get(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Unknown provider")
    try:
        recs = await provider.get_recommendations(title_id=title_id, limit=limit)
    except NotImplementedError:
        recs = None
    if not recs:
        raise HTTPException(status_code=404, detail="Recommendations not found")
    return recs


@router.get("/{ref}/reviews", response_model=ReviewsResponse)
async def get_reviews(
    ref: str,
    limit: int = Query(default=20, ge=1, le=50),
) -> ReviewsResponse:
    try:
        provider_name, title_id = _parse_ref(ref)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    provider = registry.get(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Unknown provider")
    try:
        reviews = await provider.get_reviews(title_id=title_id, limit=limit)
    except NotImplementedError:
        reviews = None
    if not reviews:
        raise HTTPException(status_code=404, detail="Reviews not found")
    return reviews
