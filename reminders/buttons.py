from RPi import GPIO


class Buttons:

    # sets up buttons with handler provided
    # handler is a function taking the letter of the button pressed
    @staticmethod
    def setup_buttons(handler):
        # BCM numbering scheme
        BUTTONS = {5: "a", 6: "b", 16: "x", 24: "y"}

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(list(BUTTONS.keys()), GPIO.IN, pull_up_down=GPIO.PUD_UP)

        for pin in BUTTONS:
            GPIO.add_event_detect(pin, GPIO.FALLING, lambda x: handler(BUTTONS[x]), bouncetime=200)
