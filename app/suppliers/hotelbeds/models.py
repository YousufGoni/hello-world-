from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class HBStay(BaseModel):
    checkIn: str
    checkOut: str


class HBOccupancy(BaseModel):
    rooms: int
    adults: int
    children: int


class HBDestination(BaseModel):
    code: str


class HBHotels(BaseModel):
    hotel: list[int]


class HBSearchRequest(BaseModel):
    stay: HBStay
    occupancies: list[HBOccupancy]
    destination: HBDestination | None = None
    hotels: HBHotels | None = None

    model_config = ConfigDict(populate_by_name=True)


class HBCancellationPolicy(BaseModel):
    amount: str | None = None
    from_: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class HBRate(BaseModel):
    rateKey: str
    rateType: str
    net: Decimal
    currency: str
    boardCode: str
    boardName: str
    cancellationPolicies: list[dict] = []


class HBRoom(BaseModel):
    code: str
    name: str
    rates: list[HBRate]


class HBHotel(BaseModel):
    code: int
    name: str
    categoryCode: str | None = None
    destinationCode: str | None = None
    minRate: Decimal
    maxRate: Decimal
    currency: str
    rooms: list[HBRoom] = []
