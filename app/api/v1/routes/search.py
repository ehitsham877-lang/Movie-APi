from fastapi import APIRouter, Query

from app.models.api import SearchResponse, TitleType
from app.services.registry import registry

router = APIRouter(prefix="/search")


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(min_length=1, max_length=200),
    type: TitleType | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
) -> SearchResponse:
    results = []
    for provider in registry.providers():
        results.extend(await provider.search(query=q, title_type=type, limit=limit))
        if len(results) >= limit:
            break
    return SearchResponse(results=results[:limit])

