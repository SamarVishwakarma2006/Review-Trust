"""Single-process request budgets, safe error responses and bounded in-memory admission."""

import asyncio
import hashlib
import hmac
import logging
import math
import os
import secrets
import time
import uuid
from collections import OrderedDict
from dataclasses import asdict
from urllib.parse import urlsplit

import anyio
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from starlette.datastructures import MutableHeaders
from starlette.responses import JSONResponse

from app.ingestion import ReviewInputError
from app.results import ErrorDetail, ErrorResponse
from app.schemas import MAX_BODY_BYTES

ANALYSIS_PATHS = {"/v1/analyze", "/v1/analyze/csv"}
_LOGGER = logging.getLogger("reviewtrust.api")


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", hide_input_in_errors=True)
    allowed_origins: tuple[str, ...] = ("http://127.0.0.1:3000", "http://localhost:3000")
    rate_per_minute: int = Field(default=10, ge=1, le=600)
    rate_burst: int = Field(default=2, ge=1, le=100)
    limiter_capacity: int = Field(default=10_000, ge=1, le=10_000)
    max_concurrent: int = Field(default=2, ge=1, le=2)
    timeout_seconds: float = Field(default=10, ge=0.01, le=30, allow_inf_nan=False)

    @field_validator("allowed_origins")
    @classmethod
    def exact_origins(cls, origins):
        if len(origins) > 10:
            raise ValueError("At most 10 CORS origins are allowed.")
        for origin in origins:
            if not origin.isascii() or any(
                character.isspace() or ord(character) < 32 for character in origin
            ):
                raise ValueError("Use an ASCII origin without whitespace or control characters.")
            parsed = urlsplit(origin)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or parsed.username
                or parsed.password
                or parsed.path
                or parsed.query
                or parsed.fragment
                or "*" in origin
            ):
                raise ValueError("CORS origins must be exact HTTP(S) origins without paths.")
            try:
                parsed.port
            except ValueError:
                raise ValueError("CORS origin port is invalid.") from None
        return tuple(dict.fromkeys(origins))

    @model_validator(mode="after")
    def burst_within_rate(self):
        if self.rate_burst > self.rate_per_minute:
            raise ValueError("Burst cannot exceed the configured refill rate.")
        return self

    @classmethod
    def from_env(cls):
        values = {}
        for name in (
            "rate_per_minute",
            "rate_burst",
            "limiter_capacity",
            "max_concurrent",
            "timeout_seconds",
        ):
            value = os.environ.get("REVIEWTRUST_" + name.upper())
            if value is not None:
                values[name] = value
        origins = os.environ.get("REVIEWTRUST_ALLOWED_ORIGINS")
        if origins is not None:
            values["allowed_origins"] = tuple(
                item.strip() for item in origins.split(",") if item.strip()
            )
        return cls.model_validate(values)


class Controls:
    """Used only on the serving event loop; no await occurs during state mutations."""

    # ponytail: process-local budgets; verify shared edge enforcement before adding workers.

    def __init__(self, settings: Settings):
        self.settings = settings
        self.active = 0
        self._key = secrets.token_bytes(32)
        self._clients = OrderedDict()

    def rate_check(self, client: str, now: float) -> None:
        while self._clients and now - next(iter(self._clients.values()))[1] >= 60:
            self._clients.popitem(last=False)
        key = hmac.new(self._key, client.encode(), hashlib.sha256).digest()
        if key not in self._clients and len(self._clients) >= self.settings.limiter_capacity:
            raise ReviewInputError(
                "limiter_capacity", "Request capacity reached; try again later.", 429
            )
        tokens, previous = self._clients.get(key, (self.settings.rate_burst, now))
        tokens = min(
            self.settings.rate_burst, tokens + (now - previous) * self.settings.rate_per_minute / 60
        )
        self._clients[key] = (tokens, now)
        self._clients.move_to_end(key)
        if tokens < 1:
            raise ReviewInputError(
                "rate_limit", "Too many analysis requests; try again later.", 429
            )
        self._clients[key] = (tokens - 1, now)


def error_response(error: ReviewInputError, request_id: str, retry_after: int | None = None):
    body = ErrorResponse(
        error=ErrorDetail(
            code=error.code,
            message=str(error),
            fields=[asdict(item) for item in error.fields],
            total_errors=error.total_errors,
            request_id=request_id,
        )
    )
    headers = {"Retry-After": str(retry_after)} if retry_after is not None else {}
    return JSONResponse(
        body.model_dump(mode="json"), status_code=error.status_code, headers=headers
    )


async def _read_body(scope, receive, deadline):
    headers = scope["headers"]
    lengths = [value for key, value in headers if key.lower() == b"content-length"]
    if len(lengths) > 1 or (lengths and (not lengths[0].isdigit() or len(lengths[0]) > 10)):
        raise ReviewInputError(
            "content_length", "Content-Length must be a single nonnegative integer.", 400
        )
    expected = int(lengths[0]) if lengths else None
    if expected is not None and expected > MAX_BODY_BYTES:
        raise ReviewInputError("body_limit", "Input exceeds the byte limit.", 413)
    data = bytearray()
    with anyio.fail_after(max(0, deadline - time.monotonic())):
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                raise ReviewInputError("client_disconnected", "Request body was interrupted.", 400)
            chunk = message.get("body", b"")
            if len(data) + len(chunk) > MAX_BODY_BYTES:
                raise ReviewInputError("body_limit", "Input exceeds the byte limit.", 413)
            data.extend(chunk)
            if not message.get("more_body", False):
                break
    if expected is not None and len(data) != expected:
        raise ReviewInputError(
            "content_length", "Request body length does not match Content-Length.", 400
        )
    return bytes(data)


class RequestBoundary:
    def __init__(self, app, settings: Settings, controls: Controls):
        self.app, self.settings, self.controls = app, settings, controls

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        request_id = uuid.uuid4().hex
        state = scope.setdefault("state", {})
        state["request_id"] = request_id
        origin = None
        admitted = False
        started = False

        async def safe_send(message):
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
                headers = MutableHeaders(scope=message)
                headers["Cache-Control"] = "no-store"
                headers["X-Request-ID"] = request_id
                headers["X-Content-Type-Options"] = "nosniff"
                headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
                headers["Referrer-Policy"] = "no-referrer"
                if origin in self.settings.allowed_origins:
                    headers["Access-Control-Allow-Origin"] = origin
                    headers["Access-Control-Expose-Headers"] = "X-Request-ID, Retry-After"
                    if "origin" not in headers.get("vary", "").lower().split(", "):
                        headers.add_vary_header("Origin")
            await send(message)

        try:
            if (
                len(scope["headers"]) > 64
                or sum(len(k) + len(v) for k, v in scope["headers"]) > 8192
            ):
                raise ReviewInputError("header_limit", "Request headers exceed the limit.", 413)
            for name in (b"origin", b"content-type", b"content-encoding"):
                if sum(key.lower() == name for key, _ in scope["headers"]) > 1:
                    raise ReviewInputError("duplicate_header", "Ambiguous request headers.", 400)
            origin = next(
                (
                    value.decode("latin-1")
                    for key, value in scope["headers"]
                    if key.lower() == b"origin"
                ),
                None,
            )
            if origin is not None and origin not in self.settings.allowed_origins:
                raise ReviewInputError(
                    "origin_not_allowed", "This request origin is not allowed.", 403
                )
            if scope["method"] == "POST" and scope["path"] in ANALYSIS_PATHS:
                client = scope.get("client")
                self.controls.rate_check(client[0] if client else "unknown", time.monotonic())
                if self.controls.active >= self.settings.max_concurrent:
                    raise ReviewInputError(
                        "analysis_busy", "Analysis capacity reached; try again shortly.", 503
                    )
                self.controls.active += 1
                admitted = True
                state["deadline"] = time.monotonic() + self.settings.timeout_seconds
                encoding = next(
                    (
                        v.lower().strip()
                        for k, v in scope["headers"]
                        if k.lower() == b"content-encoding"
                    ),
                    b"identity",
                )
                if encoding != b"identity":
                    raise ReviewInputError(
                        "content_encoding", "Compressed request bodies are not supported.", 415
                    )
                state["body"] = await _read_body(scope, receive, state["deadline"])
            await self.app(scope, receive, safe_send)
        except ReviewInputError as error:
            retry = (
                (
                    60
                    if error.code == "limiter_capacity"
                    else math.ceil(60 / self.settings.rate_per_minute)
                )
                if error.status_code == 429
                else None
            )
            await error_response(error, request_id, retry)(scope, receive, safe_send)
        except TimeoutError:
            await error_response(
                ReviewInputError("request_timeout", "Request exceeded its time budget.", 503),
                request_id,
            )(scope, receive, safe_send)
        except Exception:
            # Never log exception details or re-raise raw validation/parser payloads to Uvicorn.
            _LOGGER.error("internal_error request_id=%s", request_id)
            if not started:
                await error_response(
                    ReviewInputError("internal_error", "Analysis could not be completed.", 500),
                    request_id,
                )(scope, receive, safe_send)
        finally:
            state.pop("body", None)
            if admitted:
                worker = state.pop("worker", None)
                if worker is not None and not worker.done():

                    def release(task):
                        if not task.cancelled():
                            # Consume failures even if the client has disconnected.
                            task.exception()
                        self.controls.active -= 1

                    worker.add_done_callback(release)
                else:
                    self.controls.active -= 1


async def run_worker(request, work):
    # Shielding plus Boundary's completion callback holds admission until CPU work actually ends.
    task = asyncio.create_task(anyio.to_thread.run_sync(work))
    request.state.worker = task
    return await asyncio.shield(task)
