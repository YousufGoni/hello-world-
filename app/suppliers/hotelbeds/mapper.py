from datetime import datetime, timezone

from app.models.response import HotelResult, RateOption
from app.suppliers.hotelbeds.models import HBHotel


def map_hotel(hb_hotel: HBHotel) -> HotelResult:
    rates: list[RateOption] = []
    for room in hb_hotel.rooms:
        for rate in room.rates:
            rates.append(RateOption(
                supplier="hotelbeds",
                rate_key=rate.rateKey,
                room_type=room.name,
                board_type=rate.boardCode,
                price=rate.net,
                currency=rate.currency,
                cancellation_policy=_summarise_cancellation(rate.cancellationPolicies),
            ))
    return HotelResult(
        hotel_code=str(hb_hotel.code),
        hotel_name=hb_hotel.name,
        category_code=hb_hotel.categoryCode,
        destination_code=hb_hotel.destinationCode,
        rates=rates,
        min_rate=hb_hotel.minRate,
        currency=hb_hotel.currency,
    )


def _summarise_cancellation(policies: list[dict]) -> str | None:
    if not policies:
        return None
    free_cancel_dates = []
    for policy in policies:
        amount = policy.get("amount")
        from_date = policy.get("from")
        if amount and float(amount) == 0.0 and from_date:
            free_cancel_dates.append(from_date)
    if free_cancel_dates:
        earliest = min(free_cancel_dates)
        try:
            dt = datetime.fromisoformat(earliest.replace("Z", "+00:00"))
            return f"Free cancellation until {dt.strftime('%Y-%m-%d')}"
        except ValueError:
            return f"Free cancellation until {earliest}"
    return "Non-refundable"
