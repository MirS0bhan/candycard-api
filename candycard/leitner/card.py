from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as sSession

from candycard.models import CardBase, CardCreate, CardResponse, TokenData
from candycard.auth import get_current_user
from candycard.db import get_session, Card, Deck

from .deck import get_user_deck

router = APIRouter()

Token = Annotated[TokenData, Depends(get_current_user)]
Session = Annotated[sSession, Depends(get_session)]


async def get_user_card(deck: Deck = Depends(get_user_deck)):
    return deck.cards


@router.get("/", response_model=List[CardResponse])
def get_card(cards: List[Card] = Depends(get_user_card)):
    return cards


@router.get("/{card_id}", response_model=CardResponse)
def get_card(card_id: int, user: Token, session: Session):
    # Query a card for the current user
    card = session.query(Card).filter(Card.id == card_id, Card.user_id == user.username).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    return CardResponse.model_validate(card)  # Assuming CardResponse is a Pydantic model


@router.delete("/{card_id}", response_model=CardResponse)
def delCard(
        card_id: int,
        user: TokenData = Depends(get_current_user),
        session: Session = Depends(get_session)
) -> CardResponse:
    # Delete a card for the current user
    card = session.query(Card).filter(Card.id == card_id, Card.user_id == user.username).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    session.delete(card)
    session.commit()
    return CardResponse.from_orm(card)  # Return the deleted card


@router.post("/", response_model=CardResponse)
def pstCard(
        card: CardCreate,  # Assuming CardBase is a Pydantic model for creating new cards
        user: TokenData = Depends(get_current_user),
        session: sSession = Depends(get_session)
) -> CardResponse:
    # Create a new card for the current user
    new_card = Card(**card.model_dump())  # Add user_id to the new card
    session.add(new_card)
    session.commit()
    session.refresh(new_card)
    return new_card  # Return the created card


@router.put("/{card_id}", response_model=CardResponse)
def putCard(
        card_id: int,
        updated_card: CardBase,  # Assuming CardBase is used for updates
        user: TokenData = Depends(get_current_user),
        session: Session = Depends(get_session)
) -> CardResponse:
    # Update a card for the current user
    card = session.query(Card).filter(Card.id == card_id, Card.user_id == user.username).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Update fields
    for key, value in updated_card.dict(exclude_unset=True).items():
        setattr(card, key, value)

    session.commit()
    session.refresh(card)
    return CardResponse.from_orm(card)  # Return the updated card