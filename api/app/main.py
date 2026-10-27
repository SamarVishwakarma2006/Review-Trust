"""Development foundation. Review ingestion and analysis arrive in later steps."""

from typing import Literal

from fastapi import FastAPI, Response
from pydantic import BaseModel

app = FastAPI(title="ReviewTrust API", docs_url=None, redoc_url=None, openapi_url=None)


class DevelopmentStatus(BaseModel):
    service: Literal["ReviewTrust API"] = "ReviewTrust API"
    status: Literal["development"] = "development"


@app.get("/", response_model=DevelopmentStatus)
def development_status(response: Response) -> DevelopmentStatus:
    response.headers["Cache-Control"] = "no-store"
    return DevelopmentStatus()
