from fastapi import APIRouter, Depends

from candycard.middleware import rate_limit_builder

from .deck import router as deck_router
from .card import router as card_router

router = APIRouter(
    dependencies=[
        Depends(rate_limit_builder(30, 60, 1024))
    ]
)


deck_router.include_router(card_router, prefix="/{deck_id}/card", tags=["cards"])
router.include_router(deck_router, prefix="/deck", tags=["decks & cards"])
