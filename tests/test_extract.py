import unittest
from extract import Booking, missing_fields

class TestBooking(unittest.TestCase):
    def test_missing_is_not_silently_filled(self):
        b = Booking(is_booking_request=True, origin='CUN airport')
        self.assertIn('pickup_date', missing_fields(b))
        self.assertIn('adults', missing_fields(b))
    def test_round_trip_requires_return(self):
        b = Booking(is_booking_request=True, origin='Airport', destination='Hotel',
                    travel_type='round_trip', pickup_date='2026-12-01',
                    pickup_time='13:00', adults=2)
        self.assertIn('return_date', missing_fields(b))

if __name__ == '__main__':
    unittest.main()
