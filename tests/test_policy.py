from datetime import date
from extract import Booking
from policy import assess

BASE = dict(is_booking_request=True, explicit_confirmation=True, needs_review=False,
            customer_name='Test Client', customer_email='test@example.com',
            contact_phone='+525551234567', vehicle_type='Standard Minivan', travel_type='one_way',
            origin='Cancun Airport', destination='Hotel',
            pickup_date='2027-01-10', pickup_time='14:30', adults=2)

def test_valid_booking():
    assert assess(Booking(**BASE), today=date(2026, 10, 27)) == []

def test_no_confirmation_blocked():
    assert any('confirmation' in x for x in assess(Booking(**{**BASE, 'explicit_confirmation':False}), date(2026,10,27)))

def test_quote_blocked():
    assert assess(Booking(**{**BASE, 'quotation_only': True}), date(2026,10,27))

def test_missing_phone_blocked():
    assert assess(Booking(**{**BASE, 'contact_phone': None}), date(2026,10,27))

def test_past_date_blocked():
    assert assess(Booking(**{**BASE, 'pickup_date': '2025-01-10'}), date(2026,10,27))


def test_existing_reservation_blocked():
    assert any('duplicate' in x for x in assess(Booking(**{**BASE, 'existing_reservation':True}),date(2026,10,27)))

def test_missing_vehicle_blocked():
    assert any('Vehicle' in x for x in assess(Booking(**{**BASE,'vehicle_type':None}),date(2026,10,27)))

def test_conflicting_details_blocked():
    assert any('Conflicting' in x for x in assess(Booking(**{**BASE,'conflicting_details':True}),date(2026,10,27)))
