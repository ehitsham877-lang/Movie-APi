from fastapi import APIRouter

from app.services.registry import registry

router = APIRouter(prefix="/providers")


@router.get("")
def list_providers() -> dict:
    return {"providers": registry.list_provider_names()}

