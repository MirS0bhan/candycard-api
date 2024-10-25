from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db import User, get_session
from models import UserData, TokenData, Token
from config import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from errors import credentials_exception, registered_user, incorrect_user_data

router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Default expiration

    to_encode.update({"exp": expire}) # add expire time to token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Dependency to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData(**payload)
        if token_data.username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return token_data


# Authentication routes
@router.post("/signup", response_model=Token)
async def signup(user: UserData, session: Session = Depends(get_session)):
    # Check if user already exists
    existing_user = session.query(User).filter(User.username == user.username).one_or_none()
    if existing_user:
        raise registered_user

    # Hash the password
    hashed_password = hash_password(user.password)

    # Store user in database
    new_user = User(**user.model_dump(), hashed_password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)  # Refresh to get the new user's ID

    # Create access token
    access_token = await create_user_access_token(new_user)

    return Token(access_token=access_token, token_type="bearer")


async def create_user_access_token(user: User):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=TokenData(username=user.username, user_id=user.id).model_dump(),
        expires_delta=access_token_expires
    )
    return access_token


@router.post("/login", response_model=Token)
async def login(user: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    result = session.query(User).filter(User.username == user.username).one_or_none()

    if not result or not verify_password(user.password, result.hashed_password):
        raise incorrect_user_data

    access_token = await create_user_access_token(result)

    return Token(access_token=access_token, token_type="bearer")
