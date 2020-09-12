import os
from datetime import datetime

from reminders.events import Alerts
from reminders.menu import AlertMenu, Menu


class Task:
    def __init__(self, name):
        self.name = str(name)
        self.task_time = datetime.fromtimestamp(0)

    def alert(self):
        os.system("play /home/pi/reminder_pi/assets/sounds/beam_sound.wav &")
        print("Alert: " + self.name)

        to_remove = []
        for each in Menu.menu_stack:
            if isinstance(each, AlertMenu) and each.task == self:
                to_remove.append(each)
        for each in to_remove:
            Menu.menu_stack.remove(each)
        Menu.menu_stack.append(AlertMenu(self))
        Menu.current().display()

    def delay(self, delta):
        print("going to delay now")
        self.task_time = max(self.task_time, datetime.now()) + delta
        Alerts.add_to_schedule(self)
        print("added back to schedule")


class NamedTask(Task):
    def __init__(self, name, task_time):
        super().__init__(name)
        self.task_time = task_time


class CountdownTimer(Task):
    def __init__(self, task_time):
        super().__init__("Countdown Timer")
        self.task_time = task_time
