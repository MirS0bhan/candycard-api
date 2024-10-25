from typing import List, Annotated

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session as sSession

from candycard.auth import get_current_user
from candycard.db import get_session, Deck
from candycard.models import DeckBase, DeckResponse, TokenData

router = APIRouter()

Token = Annotated[TokenData, Depends(get_current_user)]
Session = Annotated[sSession, Depends(get_session)]


async def get_user_deck(deck_id: int, token: Token, session: Session) -> Deck | None:
    """Dependency to check if a deck exists and is owned by the current user"""
    db_deck = session.get(Deck, deck_id)
    if not db_deck or db_deck.user_id != token.user_id:
        raise HTTPException(status_code=404, detail="Deck not found")
    return db_deck

user_deck = Annotated[Deck, Depends(get_user_deck)]


@router.post("/")
async def create_deck(deck: DeckBase, token: Token, session: Session):
    db_deck = Deck(**deck.model_dump(), user_id=token.user_id)  # Adjusted to match SQLAlchemy model
    session.add(db_deck)
    session.commit()
    session.refresh(db_deck)
    return db_deck


@router.get("/", response_model=List[DeckResponse])
async def read_decks(token: Token, session: Session):
    decks = session.query(Deck).filter(Deck.user_id == token.user_id).all()
    return decks


@router.get("/", response_model=List[DeckResponse])
async def read_decks(token: Token, session: Session):
    """ return all user decks """
    decks = session.query(Deck).filter(Deck.user_id == token.user_id).all()
    return decks


@router.get("/{deck_id}")
async def read_deck(deck: Annotated[Deck, Depends(get_user_deck)]) -> DeckResponse:
    return deck


@router.put("/{deck_id}")
async def update_deck(
    deck: DeckBase, db_deck: user_deck, session: Session
):
    # Update the fields
    db_deck.name = deck.name
    db_deck.description = deck.description

    session.commit()  # No need to add again since we are updating
    session.refresh(db_deck)
    return db_deck


@router.delete("/{deck_id}")
async def delete_deck(
    db_deck: user_deck, session: Session
) -> DeckResponse:
    session.delete(db_deck)
    session.commit()
    return db_deck
