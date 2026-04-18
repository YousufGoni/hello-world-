import asyncio
import uuid
from decimal import Decimal

from app.models.request import RatesSearchRequest
from app.models.response import HotelResult, RatesSearchResponse, SupplierError
from app.suppliers.base import SupplierResult
from app.suppliers.registry import SupplierRegistry


class AggregatorService:
    def __init__(self, registry: SupplierRegistry, timeout: float) -> None:
        self._registry = registry
        self._timeout = timeout

    async def search(self, request: RatesSearchRequest) -> RatesSearchResponse:
        suppliers = self._registry.all()
        tasks = [
            asyncio.wait_for(s.search(request), timeout=self._timeout)
            for s in suppliers
        ]
        raw_results: list[SupplierResult | BaseException] = await asyncio.gather(
            *tasks, return_exceptions=True
        )

        all_hotels: dict[str, HotelResult] = {}
        errors: list[SupplierError] = []

        for result in raw_results:
            if isinstance(result, BaseException):
                errors.append(SupplierError(
                    supplier="unknown",
                    error_code="TIMEOUT",
                    message=str(result),
                ))
                continue
            if result.error:
                errors.append(result.error)
                continue
            for hotel in result.hotels:
                if hotel.hotel_code in all_hotels:
                    existing = all_hotels[hotel.hotel_code]
                    existing.rates.extend(hotel.rates)
                    existing.min_rate = min(r.price for r in existing.rates)
                else:
                    all_hotels[hotel.hotel_code] = hotel

        hotel_list = self._flag_best_rates(list(all_hotels.values()))

        return RatesSearchResponse(
            search_id=str(uuid.uuid4()),
            hotels=hotel_list,
            total_hotels=len(hotel_list),
            currency=request.currency,
            errors=errors,
        )

    def _flag_best_rates(self, hotels: list[HotelResult]) -> list[HotelResult]:
        for hotel in hotels:
            if not hotel.rates:
                continue
            cheapest_price = min(r.price for r in hotel.rates)
            flagged = False
            for rate in hotel.rates:
                if not flagged and rate.price == cheapest_price:
                    rate.is_best_rate = True
                    flagged = True
                else:
                    rate.is_best_rate = False
        return sorted(hotels, key=lambda h: h.min_rate)
