from datetime import date
from pydantic import BaseModel, Field, model_validator


class Occupancy(BaseModel):
    rooms: int = Field(ge=1, le=9)
    adults: int = Field(ge=1, le=9)
    children: int = Field(ge=0, le=9, default=0)


class RatesSearchRequest(BaseModel):
    check_in: date
    check_out: date
    occupancies: list[Occupancy] = Field(min_length=1)
    destination_code: str | None = None
    hotel_codes: list[str] | None = None
    currency: str = "EUR"

    @model_validator(mode="after")
    def check_destination_or_hotels(self) -> "RatesSearchRequest":
        if not self.destination_code and not self.hotel_codes:
            raise ValueError("Either destination_code or hotel_codes must be provided")
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")
        return self
