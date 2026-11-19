from datetime import datetime

try:
    import RPi.GPIO as GPIO
except:
    import mock.GPIO as GPIO

try:
    import SDL_DS3231
except:
    import mock.SDL_DS3231 as SDL_DS3231

class ParkingGarage:

    # Pin number declarations
    INFRARED_PIN1 = 11
    INFRARED_PIN2 = 12
    INFRARED_PIN3 = 13
    SERVO_PIN = 16
    LED_PIN = 18

    def __init__(self):
        # Mantieni le eventuali righe già presenti nel costruttore originale
        GPIO.setup(self.INFRARED_PIN1, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN2, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN3, GPIO.IN)

    def check_occupancy(self, pin: int) -> bool:
        valid_pins = (self.INFRARED_PIN1, self.INFRARED_PIN2, self.INFRARED_PIN3)
        if pin not in valid_pins:
            raise ParkingGarageError(f"Invalid infrared sensor pin: {pin}")

        return not bool(GPIO.input(pin))

    def get_number_occupied_spots(self) -> int:
        # See User Story #2
        pass

    def calculate_parking_fee(self, entry_time: datetime) -> float:
        # See User Story #3
        pass

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
