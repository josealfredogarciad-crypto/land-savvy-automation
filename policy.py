"""Hard gates before live submission; deliberately fail closed."""
from datetime import date
from extract import Booking, missing_fields


def assess(b: Booking, today: date | None = None) -> list[str]:
    today = today or date.today()
    issues = []
    if not b.is_booking_request:
        issues.append('Not an explicit booking request')
    if not b.explicit_confirmation:
        issues.append('No explicit confirmation to book')
    if b.existing_reservation:
        issues.append('Existing reservation found; duplicate risk')
    if b.conflicting_details:
        issues.append('Conflicting booking details')
    if not b.vehicle_type:
        issues.append('Vehicle selection missing')
    if b.quotation_only:
        issues.append('Quote-only inquiry')
    if b.modification_or_cancellation:
        issues.append('Existing booking modification/cancellation')
    if b.needs_review:
        issues.append('AI marked request for review')
    issues.extend(f'Missing field: {name}' for name in missing_fields(b))
    for field in ('customer_name', 'customer_email', 'contact_phone'):
        if not getattr(b, field):
            issues.append(f'Missing field: {field}')
    if b.adults is not None and b.children is not None and b.adults + b.children == 0:
        issues.append('Passenger count is zero')
    if b.pickup_date:
        try:
            if date.fromisoformat(b.pickup_date) < today:
                issues.append('Travel date is in the past')
        except ValueError:
            issues.append('Invalid date')
    if b.travel_type not in ('one_way', 'round_trip'):
        issues.append('Travel type not validated')
    return issues
