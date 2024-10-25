from fastapi import FastAPI

from auth import router as auth_router
from leitner import router as leitner_router


app = FastAPI()


app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(leitner_router, prefix="/leitner", tags=["leitner"])
