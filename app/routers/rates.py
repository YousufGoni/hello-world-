from fastapi import APIRouter, Depends, HTTPException, Request

from app.models.request import RatesSearchRequest
from app.models.response import RatesSearchResponse
from app.services.aggregator import AggregatorService

router = APIRouter(prefix="/rates", tags=["rates"])


def get_aggregator(request: Request) -> AggregatorService:
    return request.app.state.aggregator


@router.post(
    "/search",
    response_model=RatesSearchResponse,
    summary="Search hotel availability and compare rates",
    responses={
        422: {"description": "Validation error (missing or invalid fields)"},
        503: {"description": "All suppliers unavailable"},
    },
)
async def search_rates(
    body: RatesSearchRequest,
    aggregator: AggregatorService = Depends(get_aggregator),
) -> RatesSearchResponse:
    response = await aggregator.search(body)
    if response.errors and not response.hotels:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "All suppliers returned errors",
                "errors": [e.model_dump() for e in response.errors],
            },
        )
    return response
