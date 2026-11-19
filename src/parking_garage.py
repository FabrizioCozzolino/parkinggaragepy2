from datetime import datetime

try:
    import RPi.GPIO as GPIO
except:
    import mock.GPIO as GPIO

try:
    import SDL_DS3231
except:
    import mock.SDL_DS3231 as SDL_DS3231

import math
from datetime import datetime

class ParkingGarage:

    # Pin number declarations
    INFRARED_PIN1 = 11
    INFRARED_PIN2 = 12
    INFRARED_PIN3 = 13
    SERVO_PIN = 16
    LED_PIN = 18

    def __init__(self):
        # Configurazione pin sensori infrarossi (US #1)
        GPIO.setup(self.INFRARED_PIN1, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN2, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN3, GPIO.IN)

        # Inizializzazione modulo RTC (US #3)
        self.rtc = SDL_DS3231.SDL_DS3231()

    def check_occupancy(self, pin: int) -> bool:
        valid_pins = (self.INFRARED_PIN1, self.INFRARED_PIN2, self.INFRARED_PIN3)
        if pin not in valid_pins:
            raise ParkingGarageError(f"Invalid infrared sensor pin: {pin}")

        return not bool(GPIO.input(pin))

    def get_number_occupied_spots(self) -> int:
        pins = (self.INFRARED_PIN1, self.INFRARED_PIN2, self.INFRARED_PIN3)
        return sum(1 for pin in pins if self.check_occupancy(pin))

    def calculate_parking_fee(self, entry_time: datetime) -> float:
        exit_time = self.rtc.read_datetime()

        if exit_time < entry_time:
            raise ParkingGarageError("Exit time cannot be earlier than entry time.")

        duration_seconds = (exit_time - entry_time).total_seconds()
        hours = math.ceil(duration_seconds / 3600)

        fee = hours * 2.50

        # Sabato (5) o Domenica (6): maggiorazione del 25%
        if exit_time.weekday() in (5, 6):
            fee *= 1.25

        return fee

    def open_garage_door(self) -> None:
        # See User Story #4
        pass

    def close_garage_door(self) -> None:
        # See User Story #4
        pass

    def turn_on_red_light(self) -> None:
        # See User Story #5
        pass

    def turn_off_red_light(self) -> None:
        # See User Story #5
        pass

    def manage_red_light(self) -> None:
        # See User Story #6
        pass


    # This method is meant to show you how to release the hardware resources when the program running on real hardware ends.
    def cleanup(self) -> None:
        self.servo.stop() # Stops generating PWM on the pin
        GPIO.cleanup() # Resets every GPIO pin


class ParkingGarageError(Exception):
    pass
