from fastapi import APIRouter, HTTPException, Query

from app.models.api import TitleFullResponse, TitleType
from app.services.registry import registry

router = APIRouter(prefix="/lookup")


def _parse_ref(ref: str) -> tuple[str, str]:
    if ":" not in ref:
        raise ValueError("Title reference must be in 'provider:id' format")
    provider, title_id = ref.split(":", 1)
    return provider, title_id


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


@router.get("", response_model=TitleFullResponse)
async def lookup(
    q: str = Query(min_length=1, max_length=200),
    type: TitleType | None = Query(default=None),
    provider: str | None = Query(default=None),
) -> TitleFullResponse:
    provider_obj = registry.get(_pick_provider(provider))
    if not provider_obj:
        raise HTTPException(status_code=404, detail="Unknown provider")

    results = await provider_obj.search(query=q, title_type=type, limit=1)
    if not results:
        raise HTTPException(status_code=404, detail="No results")

    ref = f"{results[0].ref.provider}:{results[0].ref.id}"
    provider_name, title_id = _parse_ref(ref)
    provider_for_title = registry.get(provider_name)
    if not provider_for_title:
        raise HTTPException(status_code=404, detail="Unknown provider")

    title = await provider_for_title.get_title(title_id=title_id)
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")

    credits = await provider_for_title.get_credits(title_id=title_id)
    ratings = await provider_for_title.get_ratings(title_id=title_id)
    trailers = await provider_for_title.get_trailers(title_id=title_id)
    return TitleFullResponse(title=title, credits=credits, ratings=ratings, trailers=trailers)
