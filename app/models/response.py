from decimal import Decimal
from pydantic import BaseModel


class SupplierError(BaseModel):
    supplier: str
    error_code: str
    message: str


class RateOption(BaseModel):
    supplier: str
    rate_key: str | None = None
    room_type: str
    board_type: str
    price: Decimal
    currency: str
    cancellation_policy: str | None = None
    is_best_rate: bool = False


class HotelResult(BaseModel):
    hotel_code: str
    hotel_name: str
    category_code: str | None = None
    destination_code: str | None = None
    rates: list[RateOption]
    min_rate: Decimal
    currency: str


class RatesSearchResponse(BaseModel):
    search_id: str
    hotels: list[HotelResult]
    total_hotels: int
    currency: str
    errors: list[SupplierError] = []
