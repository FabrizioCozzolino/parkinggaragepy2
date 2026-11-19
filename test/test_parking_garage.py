import unittest
from unittest.mock import patch
from parking_garage import ParkingGarage, ParkingGarageError, GPIO


class TestParkingGarage(unittest.TestCase):

    @patch("parking_garage.GPIO.setup")
    def test_gpio_pins_configured_as_input_on_init(self, mock_setup):
        garage = ParkingGarage()
        mock_setup.assert_any_call(ParkingGarage.INFRARED_PIN1, GPIO.IN)
        mock_setup.assert_any_call(ParkingGarage.INFRARED_PIN2, GPIO.IN)
        mock_setup.assert_any_call(ParkingGarage.INFRARED_PIN3, GPIO.IN)

    @patch("parking_garage.GPIO.setup")
    @patch("parking_garage.GPIO.input")
    def test_check_occupancy_car_detected(self, mock_input, mock_setup):
        mock_input.return_value = False
        garage = ParkingGarage()

        self.assertTrue(garage.check_occupancy(ParkingGarage.INFRARED_PIN1))
        mock_input.assert_called_with(ParkingGarage.INFRARED_PIN1)

    @patch("parking_garage.GPIO.setup")
    @patch("parking_garage.GPIO.input")
    def test_check_occupancy_no_car_detected(self, mock_input, mock_setup):
        mock_input.return_value = True
        garage = ParkingGarage()

        self.assertFalse(garage.check_occupancy(ParkingGarage.INFRARED_PIN2))
        mock_input.assert_called_with(ParkingGarage.INFRARED_PIN2)

    @patch("parking_garage.GPIO.setup")
    @patch("parking_garage.GPIO.input")
    def test_check_occupancy_spot_3(self, mock_input, mock_setup):
        mock_input.return_value = False
        garage = ParkingGarage()

        self.assertTrue(garage.check_occupancy(ParkingGarage.INFRARED_PIN3))
        mock_input.assert_called_with(ParkingGarage.INFRARED_PIN3)

    @patch("parking_garage.GPIO.setup")
    def test_check_occupancy_invalid_pin_raises_error(self, mock_setup):
        garage = ParkingGarage()

        with self.assertRaises(ParkingGarageError):
            garage.check_occupancy(99)