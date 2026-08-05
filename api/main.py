"""EnviroLens FastAPI application."""

from __future__ import annotations

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.routes.v1 import router as v1_router
from integrations.dhis2_mock.router import router as dhis2_router

app = FastAPI(
    title="EnviroLens API",
    description="Environmental health data and risk intelligence platform (Verdania air-pollution MVP)",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def audit_timing(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"
    return response


app.include_router(v1_router)
app.include_router(dhis2_router)


@app.get("/")
def root():
    return {
        "name": "EnviroLens",
        "version": "0.1.0",
        "docs": "/docs",
        "api": "/api/v1",
    }
