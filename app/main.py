from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.config import settings
from app.routers import rates
from app.services.aggregator import AggregatorService
from app.suppliers.hotelbeds.adapter import HotelBedsAdapter
from app.suppliers.registry import SupplierRegistry


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    registry = SupplierRegistry()
    registry.register(HotelBedsAdapter(settings))
    # To add more suppliers: registry.register(AnotherAdapter(settings))

    app.state.aggregator = AggregatorService(
        registry=registry,
        timeout=float(settings.aggregator_concurrency_timeout_seconds),
    )
    yield
    await registry.close_all()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Hotel Rates Aggregator",
        description="Compare live hotel rates across multiple suppliers.",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.include_router(rates.router)
    return app


app = create_app()
