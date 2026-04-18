import httpx

from app.config import Settings
from app.models.request import RatesSearchRequest
from app.models.response import SupplierError
from app.suppliers.base import AbstractSupplier, SupplierResult
from app.suppliers.hotelbeds.auth import build_headers
from app.suppliers.hotelbeds.mapper import map_hotel
from app.suppliers.hotelbeds.models import (
    HBDestination,
    HBHotel,
    HBHotels,
    HBOccupancy,
    HBSearchRequest,
    HBStay,
)


class HotelBedsAdapter(AbstractSupplier):
    name = "hotelbeds"
    _SEARCH_PATH = "/hotel-api/1.0/hotels"

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.hotelbeds_api_key
        self._secret = settings.hotelbeds_secret
        self._base_url = settings.hotelbeds_base_url
        self._timeout = httpx.Timeout(settings.hotelbeds_timeout_seconds)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
            )
        return self._client

    async def search(self, request: RatesSearchRequest) -> SupplierResult:
        try:
            hb_request = self._build_request(request)
            headers = build_headers(self._api_key, self._secret)
            client = await self._get_client()

            response = await client.post(
                self._SEARCH_PATH,
                json=hb_request.model_dump(exclude_none=True),
                headers=headers,
            )
            return self._handle_response(response)

        except httpx.TimeoutException:
            return SupplierResult(error=SupplierError(
                supplier=self.name,
                error_code="TIMEOUT",
                message="HotelBeds request timed out",
            ))
        except httpx.HTTPStatusError as exc:
            return self._map_http_error(exc)
        except Exception as exc:
            return SupplierResult(error=SupplierError(
                supplier=self.name,
                error_code="UPSTREAM_ERROR",
                message=str(exc),
            ))

    def _build_request(self, request: RatesSearchRequest) -> HBSearchRequest:
        stay = HBStay(
            checkIn=request.check_in.isoformat(),
            checkOut=request.check_out.isoformat(),
        )
        occupancies = [
            HBOccupancy(rooms=o.rooms, adults=o.adults, children=o.children)
            for o in request.occupancies
        ]
        destination = HBDestination(code=request.destination_code) if request.destination_code else None
        hotels = HBHotels(hotel=[int(c) for c in request.hotel_codes]) if request.hotel_codes else None
        return HBSearchRequest(
            stay=stay,
            occupancies=occupancies,
            destination=destination,
            hotels=hotels,
        )

    def _handle_response(self, response: httpx.Response) -> SupplierResult:
        if response.status_code == 401:
            return SupplierResult(error=SupplierError(
                supplier=self.name,
                error_code="AUTH_FAILURE",
                message="Invalid API key or signature",
            ))
        if response.status_code == 429:
            return SupplierResult(error=SupplierError(
                supplier=self.name,
                error_code="RATE_LIMIT",
                message="HotelBeds rate limit exceeded",
            ))
        response.raise_for_status()

        data = response.json()
        raw_hotels = data.get("hotels", {}).get("hotels", [])
        hotels = [map_hotel(HBHotel(**h)) for h in raw_hotels]
        return SupplierResult(hotels=hotels)

    def _map_http_error(self, exc: httpx.HTTPStatusError) -> SupplierResult:
        return SupplierResult(error=SupplierError(
            supplier=self.name,
            error_code="UPSTREAM_ERROR",
            message=f"HTTP {exc.response.status_code}: {exc.response.text[:200]}",
        ))

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
