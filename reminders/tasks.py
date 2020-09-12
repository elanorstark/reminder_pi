import os
from datetime import datetime

from reminders.menu import AlertMenu, Menu


class Task:
    def __init__(self, name):
        self.name = str(name)
        self.task_time = datetime.fromtimestamp(0)

    def alert(self):
        os.system("play /home/pi/reminder_pi/assets/sounds/beam_sound.wav &")
        print("Alert: " + self.name)

        Menu.menu_stack.append(AlertMenu(self))
        Menu.current().display()


class NamedTask(Task):
    def __init__(self, name, task_time):
        super().__init__(name)
        self.task_time = task_time


class CountdownTimer(Task):
    def __init__(self, task_time):
        super().__init__("Countdown Timer")
        self.task_time = task_time
