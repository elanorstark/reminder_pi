import os
import datetime

from reminders.events import Alerts
from reminders.menu import AlertMenu, Menu


class Task:
    def __init__(self, name, time, parent_task=None):
        self.name = str(name)
        self.task_time = time
        self.parent_task = parent_task

    def alert(self):
        os.system("play /home/pi/reminder_pi/assets/sounds/beam_sound.wav > /dev/null 2>&1 &")
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
        self.task_time = max(self.task_time, datetime.datetime.now()) + delta
        Alerts.add_to_schedule(self)


class NamedTask(Task):
    def __init__(self, name, task_time, parent_task=None):
        super().__init__(name, task_time, parent_task)
        self.on = True
        self.complete = False

    def on_toggle(self):
        self.on = not self.on

    def complete_toggle(self):
        self.complete = not self.complete


class CountdownTimer(Task):
    def __init__(self, task_time):
        super().__init__("Countdown Timer")
        self.task_time = task_time
