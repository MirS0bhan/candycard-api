from typing import List
from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import relationship, MappedColumn, Mapped, Session, declarative_base, mapped_column

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    username = mapped_column(String(50), unique=True, index=True)
    full_name = mapped_column(String(50), unique=True, index=True)
    email = mapped_column(String(100), unique=True, index=True)
    hashed_password = mapped_column(String)
    created_at = mapped_column(DateTime, default=datetime.utcnow)

    decks: MappedColumn["Deck"] = relationship("Deck", back_populates="owner")


class Deck(Base):
    __tablename__ = 'decks'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    owner: Mapped[User] = relationship("User", back_populates="decks")
    cards: MappedColumn[List["Card"]] = relationship("Card", back_populates="deck")


class Card(Base):
    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    question = Column(String(500), nullable=False)
    answer = Column(String(500), nullable=False)
    last_reviewed = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=True)
    review_interval = Column(Integer, default=1)
    deck_id = Column(Integer, ForeignKey('decks.id'))

    deck: Mapped[Deck] = relationship("Deck", back_populates="cards")


engine = create_engine("postgresql://misano@localhost:5432/leitner")
Base.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session