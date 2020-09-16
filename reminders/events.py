import datetime

from RPi import GPIO
from threading import Lock, Thread
import time

_lock = Lock()

# sets up the buttons and stores which button does what
class Buttons:
    button_numbers = {5: "a", 6: "b", 16: "x", 24: "y"}

    home_menu_buttons = {"a": "home", "b": "none", "y": "none", "x": "backlight"}
    list_menu_buttons = {"a": "select", "b": "up", "y": "down", "x": "home"}
    time_menu_buttons = {"a": "next", "b": "decrease", "y": "increase", "x": "units"}
    alert_menu_buttons = {"a": "dismiss", "b": "complete", "y": "none", "x": "delay"}

    # sets up buttons with handler provided
    # handler is a function taking the letter of the button pressed
    @staticmethod
    def setup_buttons(handler):
        # stop multiple button handlers being called at once
        def lock_button_handler(pin):
            with _lock:
                handler(Buttons.button_numbers[pin])

        # BCM numbering scheme

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(list(Buttons.button_numbers.keys()), GPIO.IN, pull_up_down=GPIO.PUD_UP)

        for pin in Buttons.button_numbers:
            GPIO.add_event_detect(pin, GPIO.FALLING, lock_button_handler, bouncetime=300)


# contains a function to run in a thread
# checks the time and calls the handler at each new minute
class Clock:
    last_time = datetime.datetime.now()

    @staticmethod
    def set_up_clock(handler):
        def clock_updater():
            while True:
                time.sleep(1)
                now = datetime.datetime.now()
                if Clock.last_time.hour != now.hour or Clock.last_time.minute != now.minute:
                    Clock.last_time = now
                    with _lock:
                        handler()

        updater = Thread(target=clock_updater, daemon=True)
        updater.start()


# stores the list of scheduled items that are turned on
# manages the list to make sure items are unique and the list is in order
# contains thread to check if it's time for an alert
class Alerts:
    scheduled = []
    last_updated = datetime.datetime.fromtimestamp(0)

    @staticmethod
    def print_schedule():
        print("scheduled:", [each.name + " " + str(each.task_time) for each in Alerts.scheduled])

    @staticmethod
    def add_to_schedule(task):
        if task not in Alerts.scheduled:
            Alerts.scheduled.append(task)
            Alerts.scheduled.sort(key=lambda x: x.task_time)
        Alerts.print_schedule()

    @staticmethod
    def remove_from_schedule(task):
        if task in Alerts.scheduled:
            Alerts.scheduled.remove(task)
        Alerts.print_schedule()

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
