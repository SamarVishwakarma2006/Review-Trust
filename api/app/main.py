"""ReviewTrust's bounded, ephemeral experimental analysis API."""

from typing import Literal

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from app.analysis import analyze, check_deadline
from app.ingestion import ReviewInputError, parse_json
from app.product_api import PRODUCT_PATH, product_analysis
from app.results import AnalysisResult, ErrorResponse, Score
from app.schemas import MAX_BODY_BYTES
from app.security import Controls, RequestBoundary, Settings, error_response, run_worker
from app.uploads import content_type, parse_upload


class DevelopmentStatus(BaseModel):
    service: Literal["ReviewTrust API"] = "ReviewTrust API"
    status: Literal["development"] = "development"


class HealthStatus(BaseModel):
    status: Literal["ok"] = "ok"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings if settings is not None else Settings.from_env()
    api = FastAPI(
        title="ReviewTrust API",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        redirect_slashes=False,
    )
    api.state.settings = settings
    api.state.controls = Controls(settings)

    @api.exception_handler(HTTPException)
    async def http_error(request: Request, error: HTTPException):
        code = (
            "not_found"
            if error.status_code == 404
            else "method_not_allowed"
            if error.status_code == 405
            else "http_error"
        )
        response = error_response(
            ReviewInputError(code, "Request path or method is not supported.", error.status_code),
            request.state.request_id,
        )
        if error.status_code == 405 and error.headers:
            response.headers["Allow"] = error.headers.get("Allow", "")
        return response

    @api.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError):
        return error_response(
            ReviewInputError("invalid_request", "Correct the request format."),
            request.state.request_id,
        )

    @api.get("/", response_model=DevelopmentStatus)
    async def development_status(response: Response) -> DevelopmentStatus:
        response.headers["Cache-Control"] = "no-store"
        return DevelopmentStatus()

    @api.get("/health", response_model=HealthStatus)
    async def health() -> HealthStatus:
        return HealthStatus()

    errors = {
        status: {"model": ErrorResponse} for status in (400, 403, 413, 415, 422, 429, 500, 503)
    }

    @api.post("/v1/analyze", response_model=AnalysisResult, responses=errors)
    @api.post("/v1/analyze/csv", response_model=AnalysisResult, responses=errors)
    async def analysis(request: Request):
        data, deadline = request.state.body, request.state.deadline
        header = request.headers.get("content-type", "")
        csv_route = request.url.path == "/v1/analyze/csv"

        def work():
            check_deadline(deadline)
            if csv_route:
                batch = parse_upload(data, header, deadline)
            else:
                media, _ = content_type(header)
                if media != b"application/json":
                    raise ReviewInputError(
                        "media_type", "Use application/json for pasted reviews.", 415
                    )
                batch = parse_json(data)
            check_deadline(deadline)
            result = analyze(batch, deadline)
            # Public endpoints never expose the unvalidated offline research index.
            result.score = Score(
                status="insufficient_evidence" if result.score.reason_codes else "withheld",
                value=None,
                reason_codes=["public_score_not_validated", *result.score.reason_codes],
                evaluated_signal_ids=result.score.evaluated_signal_ids,
            )
            result.limitations.insert(
                0, "Numeric scores are withheld: public validity is unproven."
            )
            body = result.model_dump_json().encode("utf-8")
            if len(body) > 2 * MAX_BODY_BYTES:
                raise ReviewInputError("response_limit", "Result exceeds the response limit.", 413)
            check_deadline(deadline)
            return Response(body, media_type="application/json")

        return await run_worker(request, work)

    api.add_api_route(PRODUCT_PATH, product_analysis, methods=["POST"], responses=errors)

    api.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        allow_credentials=False,
        expose_headers=["X-Request-ID", "Retry-After"],
    )
    api.add_middleware(RequestBoundary, settings=settings, controls=api.state.controls)
    return api


app = create_app()
