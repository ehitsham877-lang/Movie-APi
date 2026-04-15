from fastapi import Depends, Header, HTTPException, status

from app.core.config import settings


def api_key_dependency():
    if not settings.api_key:
        return []

    async def _require_api_key(x_api_key: str | None = Header(default=None)) -> None:
        if not x_api_key or x_api_key != settings.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )

    return [Depends(_require_api_key)]

