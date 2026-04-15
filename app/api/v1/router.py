from fastapi import APIRouter

from app.api.v1.routes.browse import router as browse_router
from app.api.v1.routes.lookup import router as lookup_router
from app.api.v1.routes.people import router as people_router
from app.api.v1.routes.providers import router as providers_router
from app.api.v1.routes.search import router as search_router

router = APIRouter()

router.include_router(browse_router, tags=["browse"])
router.include_router(lookup_router, tags=["lookup"])
router.include_router(people_router, tags=["people"])
router.include_router(providers_router, tags=["providers"])
router.include_router(search_router, tags=["search"])
