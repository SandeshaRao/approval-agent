from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.quota import router as quota_router


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []
    for error in exc.errors():
        normalized = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", "Validation error"),
            "type": error.get("type", "validation_error"),
        }
        if "ctx" in error and error["ctx"]:
            normalized["ctx"] = {key: str(value) for key, value in error["ctx"].items()}
        details.append(normalized)
    return JSONResponse(status_code=400, content={"detail": details})


app = FastAPI(title="AKS Quota Auto-Approval", version="1.0.0")
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.include_router(quota_router)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}
