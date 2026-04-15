from fastapi import APIRouter, HTTPException

from app.models.api import PersonProfile
from app.services.registry import registry

router = APIRouter(prefix="/person")


def _parse_ref(ref: str) -> tuple[str, str]:
    if ":" not in ref:
        raise ValueError("Person reference must be in 'provider:id' format")
    provider, person_id = ref.split(":", 1)
    return provider, person_id


@router.get("/{ref}", response_model=PersonProfile)
async def get_person(ref: str) -> PersonProfile:
    try:
        provider_name, person_id = _parse_ref(ref)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    provider = registry.get(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail="Unknown provider")
    try:
        profile = await provider.get_person(person_id=person_id)
    except NotImplementedError:
        profile = None
    if not profile:
        raise HTTPException(status_code=404, detail="Person not found")
    return profile

