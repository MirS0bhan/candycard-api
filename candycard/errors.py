from fastapi import HTTPException

credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
)

registered_user = HTTPException(
    status_code=400,
    detail="Username already registered"
)

incorrect_user_data = HTTPException(
    status_code=401,
    detail="Incorrect username or password"
)

flowd_exception = HTTPException(
    status_code=429,
    detail="Rate limit exceeded. Try again later."
)



