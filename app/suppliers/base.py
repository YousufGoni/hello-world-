from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.models.request import RatesSearchRequest
from app.models.response import HotelResult, SupplierError


@dataclass
class SupplierResult:
    hotels: list[HotelResult] = field(default_factory=list)
    error: SupplierError | None = None


class AbstractSupplier(ABC):
    name: str

    @abstractmethod
    async def search(self, request: RatesSearchRequest) -> SupplierResult:
        """Execute availability search. Must not raise — capture errors into SupplierResult.error."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Release held resources (HTTP connections, etc.)."""
        ...
