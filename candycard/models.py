from pydantic import BaseModel, EmailStr, constr, Field
from typing import List, Optional
from datetime import datetime


# Pydantic models for request bodies

class Response(BaseModel):
    created_at: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: constr(max_length=50)
    password: str = Field(exclude=True)


class UserData(UserBase):
    email: str
    full_name: str


class UserResponse(UserBase, Response):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str
    user_id: int


class DeckBase(BaseModel):
    name: constr(max_length=100)
    description: constr(max_length=100)

    class Config:
        orm_mode = True


class DeckResponse(DeckBase, Response):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class CardBase(BaseModel):
    question: constr(max_length=500)
    answer: constr(max_length=900)
    review_interval: int = 1  # Default value


class CardCreate(CardBase):
    deck_id: int


class CardResponse(CardCreate, Response):
    id: int
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None

    class Config:
        orm_mode = True
