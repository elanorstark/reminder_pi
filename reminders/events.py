from RPi import GPIO
from threading import Lock, Thread
import time

_lock = Lock()


class Buttons:

    # sets up buttons with handler provided
    # handler is a function taking the letter of the button pressed
    @staticmethod
    def setup_buttons(handler):
        BUTTONS = {5: "a", 6: "b", 16: "x", 24: "y"}

        # stop multiple button handlers being called at once
        def lock_button_handler(pin):
            with _lock:
                handler(BUTTONS[pin])

        # BCM numbering scheme

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(list(BUTTONS.keys()), GPIO.IN, pull_up_down=GPIO.PUD_UP)

        for pin in BUTTONS:
            GPIO.add_event_detect(pin, GPIO.FALLING, lock_button_handler, bouncetime=200)


class Clock:

    @staticmethod
    def setup_clock(handler):
        def clock_updater():
            while True:
                time.sleep(5)
                with _lock:
                    handler()

        updater = Thread(target=clock_updater)
        updater.start()
