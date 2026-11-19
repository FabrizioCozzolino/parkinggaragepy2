import unittest
from unittest.mock import patch
from datetime import datetime
from parking_garage import ParkingGarage, ParkingGarageError, GPIO


class TestParkingGarage(unittest.TestCase):

    def setUp(self):
        self.setup_patcher = patch("parking_garage.GPIO.setup")
        self.input_patcher = patch("parking_garage.GPIO.input")
        self.output_patcher = patch("parking_garage.GPIO.output")
        self.pwm_patcher = patch("parking_garage.GPIO.PWM")
        self.rtc_patcher = patch("parking_garage.SDL_DS3231.SDL_DS3231")

        self.mock_setup = self.setup_patcher.start()
        self.mock_input = self.input_patcher.start()
        self.mock_output = self.output_patcher.start()
        self.mock_pwm_cls = self.pwm_patcher.start()
        self.mock_rtc_cls = self.rtc_patcher.start()

        self.addCleanup(self.setup_patcher.stop)
        self.addCleanup(self.input_patcher.stop)
        self.addCleanup(self.output_patcher.stop)
        self.addCleanup(self.pwm_patcher.stop)
        self.addCleanup(self.rtc_patcher.stop)

    # --- USER STORY 1 ---
    def test_gpio_pins_configured_as_input_on_init(self):
        garage = ParkingGarage()
        self.mock_setup.assert_any_call(ParkingGarage.INFRARED_PIN1, GPIO.IN)
        self.mock_setup.assert_any_call(ParkingGarage.INFRARED_PIN2, GPIO.IN)
        self.mock_setup.assert_any_call(ParkingGarage.INFRARED_PIN3, GPIO.IN)

    def test_check_occupancy_car_detected(self):
        self.mock_input.return_value = False
        garage = ParkingGarage()
        self.assertTrue(garage.check_occupancy(ParkingGarage.INFRARED_PIN1))
        self.mock_input.assert_called_with(ParkingGarage.INFRARED_PIN1)

    def test_check_occupancy_no_car_detected(self):
        self.mock_input.return_value = True
        garage = ParkingGarage()
        self.assertFalse(garage.check_occupancy(ParkingGarage.INFRARED_PIN2))
        self.mock_input.assert_called_with(ParkingGarage.INFRARED_PIN2)

    def test_check_occupancy_spot_3(self):
        self.mock_input.return_value = False
        garage = ParkingGarage()
        self.assertTrue(garage.check_occupancy(ParkingGarage.INFRARED_PIN3))
        self.mock_input.assert_called_with(ParkingGarage.INFRARED_PIN3)

    def test_check_occupancy_invalid_pin_raises_error(self):
        garage = ParkingGarage()
        with self.assertRaises(ParkingGarageError):
            garage.check_occupancy(99)

    # --- USER STORY 2 ---
    def test_get_number_occupied_spots_none(self):
        self.mock_input.side_effect = [True, True, True]
        garage = ParkingGarage()
        self.assertEqual(garage.get_number_occupied_spots(), 0)

    def test_get_number_occupied_spots_two(self):
        self.mock_input.side_effect = [False, True, False]
        garage = ParkingGarage()
        self.assertEqual(garage.get_number_occupied_spots(), 2)

    def test_get_number_occupied_spots_all(self):
        self.mock_input.side_effect = [False, False, False]
        garage = ParkingGarage()
        self.assertEqual(garage.get_number_occupied_spots(), 3)

    # --- USER STORY 3 ---
    def test_rtc_initialized_on_init(self):
        garage = ParkingGarage()
        self.mock_rtc_cls.assert_called_once_with()
        self.assertEqual(garage.rtc, self.mock_rtc_cls.return_value)

    def test_calculate_parking_fee_weekday_partial_hour(self):
        self.mock_rtc_cls.return_value.read_datetime.return_value = datetime(2026, 11, 16, 15, 24)
        garage = ParkingGarage()
        entry_time = datetime(2026, 11, 16, 12, 30)
        self.assertEqual(garage.calculate_parking_fee(entry_time), 7.50)

    def test_calculate_parking_fee_weekend_surcharge(self):
        self.mock_rtc_cls.return_value.read_datetime.return_value = datetime(2026, 11, 21, 18, 12)
        garage = ParkingGarage()
        entry_time = datetime(2026, 11, 21, 10, 15)
        self.assertEqual(garage.calculate_parking_fee(entry_time), 25.00)

    def test_calculate_parking_fee_sunday_exact_hours(self):
        self.mock_rtc_cls.return_value.read_datetime.return_value = datetime(2026, 11, 22, 12, 0)
        garage = ParkingGarage()
        entry_time = datetime(2026, 11, 22, 10, 0)
        self.assertEqual(garage.calculate_parking_fee(entry_time), 6.25)

    def test_calculate_parking_fee_exit_before_entry_raises_error(self):
        self.mock_rtc_cls.return_value.read_datetime.return_value = datetime(2026, 11, 16, 10, 0)
        garage = ParkingGarage()
        entry_time = datetime(2026, 11, 16, 12, 0)
        with self.assertRaises(ParkingGarageError):
            garage.calculate_parking_fee(entry_time)

    # --- USER STORY 4 ---
    def test_servo_initialized_on_init(self):
        garage = ParkingGarage()

        self.mock_setup.assert_any_call(ParkingGarage.SERVO_PIN, GPIO.OUT)
        self.mock_pwm_cls.assert_called_once_with(ParkingGarage.SERVO_PIN, 50)
        self.assertEqual(garage.servo, self.mock_pwm_cls.return_value)
        garage.servo.start.assert_called_once_with(5)
        self.assertFalse(garage.door_open)

    def test_open_garage_door(self):
        garage = ParkingGarage()
        garage.open_garage_door()

        garage.servo.ChangeDutyCycle.assert_called_once_with(10)
        self.assertTrue(garage.door_open)

    def test_close_garage_door(self):
        garage = ParkingGarage()
        garage.open_garage_door()
        garage.servo.ChangeDutyCycle.reset_mock()

        garage.close_garage_door()

        garage.servo.ChangeDutyCycle.assert_called_once_with(5)
        self.assertFalse(garage.door_open)

    # --- USER STORY 5 ---
    def test_red_light_initialized_on_init(self):
        garage = ParkingGarage()

        self.mock_setup.assert_any_call(ParkingGarage.LED_PIN, GPIO.OUT)
        self.assertFalse(garage.red_light_on)

    def test_turn_on_red_light(self):
        garage = ParkingGarage()
        garage.turn_on_red_light()

        self.mock_output.assert_called_once_with(ParkingGarage.LED_PIN, True)
        self.assertTrue(garage.red_light_on)

    def test_turn_off_red_light(self):
        garage = ParkingGarage()
        garage.turn_on_red_light()
        self.mock_output.reset_mock()

        garage.turn_off_red_light()

        self.mock_output.assert_called_once_with(ParkingGarage.LED_PIN, False)
        self.assertFalse(garage.red_light_on)