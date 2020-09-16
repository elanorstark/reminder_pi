import os
import datetime

from reminders.events import Alerts
from reminders.menu import AlertMenu, Menu


class ScheduledTask:
    today = []

    def __init__(self, name, time, parent_task=None):
        self.name = str(name)
        self.task_time = time
        self.parent_task = parent_task
        self.on = True
        self.complete = False

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
        if not self.complete:
            self.task_time = max(self.task_time, datetime.datetime.now()) + delta
            Alerts.add_to_schedule(self)

    def on_toggle(self):
        pass

    def complete_toggle(self):
        pass

    @staticmethod
    def add_to_today(task):
        if task not in ScheduledTask.today:
            ScheduledTask.today.append(task)
            ScheduledTask.today.sort(key=lambda x: x.task_time)

    @staticmethod
    def clear_out_today():
        for each in ScheduledTask.today:
            if isinstance(each, RepeatScheduledTask):
                ScheduledTask.today.remove(each)


class RepeatScheduledTask(ScheduledTask):
    def __init__(self, name, task_time, parent_task=None):
        super().__init__(name, task_time, parent_task)
        self.on = True
        Alerts.add_to_schedule(self)
        self.complete = False

    def on_toggle(self):
        self.on = not self.on
        if not self.on:
            print("remove from schedule")
            Alerts.remove_from_schedule(self)
            self.complete = False
        if self.on and not self.complete:
            print("add to")
            Alerts.add_to_schedule(self)

    def complete_toggle(self):
        self.complete = not self.complete
        if self.complete:
            print("remove from")
            Alerts.remove_from_schedule(self)
        if not self.complete and self.on:
            print("add to")
            Alerts.add_to_schedule(self)


class CountdownTimer(ScheduledTask):
    def __init__(self, task_time):
        super().__init__("Countdown Timer", task_time)
