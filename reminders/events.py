import datetime

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
            GPIO.add_event_detect(pin, GPIO.FALLING, lock_button_handler, bouncetime=300)


class Clock:
    last_time = datetime.datetime.now()
    handlers = []

    @staticmethod
    def set_up_clock():
        def clock_updater():
            while True:
                time.sleep(1)
                now = datetime.datetime.now()
                if Clock.last_time.hour != now.hour or Clock.last_time.minute != now.minute:
                    Clock.last_time = now
                    with _lock:
                        for handler in Clock.handlers:
                            print(handler)
                            handler()

        updater = Thread(target=clock_updater, daemon=True)
        updater.start()

    @staticmethod
    def add_clock_task(handler):
        Clock.handlers.append(handler)


class Alerts:
    scheduled = []
    last_updated = datetime.datetime.fromtimestamp(0)

    @staticmethod
    def add_to_schedule(task):
        if task not in Alerts.scheduled:
            Alerts.scheduled.append(task)
            Alerts.scheduled.sort(key=lambda x: x.task_time)
        print("scheduled:", Alerts.scheduled)

    @staticmethod
    def set_up_alerts():
        def alert_checker():
            alert_tf = False
            while True:
                time.sleep(5)
                with _lock:
                    if len(Alerts.scheduled) > 0 and datetime.datetime.now() >= Alerts.scheduled[0].task_time:
                        alert_now = Alerts.scheduled.pop(0)
                        alert_tf = True
                if alert_tf:
                    alert_tf = False
                    alert_now.alert()

        updater = Thread(target=alert_checker(), daemon=True)
        updater.start()