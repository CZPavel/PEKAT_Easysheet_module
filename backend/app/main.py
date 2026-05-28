"""Entrypoint FastAPI backendu pro PEKAT Easysheet Module."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router

app = FastAPI(
    title="PEKAT Easysheet Module",
    version="0.1.0",
    description="Spreadsheet-like decision bridge for PEKAT VISION.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


if __name__ == "__main__":
    # Lok?ln? v?vojov? spu?t?n? bez nutnosti pamatovat si uvicorn p??kaz.
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
