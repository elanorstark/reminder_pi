import os
import datetime

from reminders.data import DataIO
from reminders.events import Alerts
from reminders.menu import AlertMenu, Menu
from reminders.planned_tasks import RepeatTask


class ScheduledTask:
    today = []
    last_updated = datetime.datetime.fromtimestamp(0)

    def __init__(self, name, time, on=True, complete=False, parent_task=None):
        self.name = str(name)
        self._task_time = time
        self.parent_task = parent_task
        self.on = on
        self.complete = complete

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
            self._task_time = max(self._task_time, datetime.datetime.now()) + delta
            Alerts.add_to_schedule(self)

    def on_toggle(self):
        pass

    def complete_toggle(self):
        pass

    def get_task_time(self):
        return self._task_time

    def set_task_time(self, task_time):
        self._task_time = task_time

    @staticmethod
    def add_to_today(task):
        if task not in ScheduledTask.today:
            ScheduledTask.today.append(task)
            ScheduledTask.today.sort(key=lambda x: x.get_task_time())

    @staticmethod
    def clear_out_today():
        for each in ScheduledTask.today:
            if isinstance(each, RepeatScheduledTask):
                ScheduledTask.today.remove(each)

    @staticmethod
    def write_out_today():
        DataIO.write_out_today(ScheduledTask.today,
                               datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))

    @staticmethod
    def add_to_history(today, date):
        new_log = {"tasks": today, "date": [date.year, date.month, date.day]}
        DataIO.add_local_history(new_log)

    @staticmethod
    def set_up_today():
        update_start = datetime.datetime.now()

        ScheduledTask.clear_out_today()

        tasks_log, date_log = DataIO.read_in_today()
        date_today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if (date_today.day, date_today.month, date_today.year) == (date_log.day, date_log.month, date_log.year):
            print(date_log, tasks_log)
            for task in tasks_log:
                t = task["_task_time"]
                task_time = datetime.datetime(year=t[0], month=t[1], day=t[2], hour=t[3], minute=t[4])
                ScheduledTask.today.append(
                    ScheduledTask(task["name"], task_time, on=task["on"], complete=task["complete"]))
            ScheduledTask.last_updated = date_log

        else:
            if tasks_log:
                ScheduledTask.add_to_history(tasks_log, date_log)
            ScheduledTask.today_from_daily_tasks()

        for task in ScheduledTask.today:
            if task.on and not task.complete:
                Alerts.add_to_schedule(task)

        ScheduledTask.last_updated = update_start

    @staticmethod
    def today_from_daily_tasks():
        time_now = datetime.datetime.now()
        midnight_today = time_now.replace(hour=0, minute=0, second=0, microsecond=0)

        for task in RepeatTask.tasks:
            if task.task_days[midnight_today.weekday()]:
                scheduled_time = midnight_today.replace(hour=task.task_time.hour, minute=task.task_time.minute)
                new_task = RepeatScheduledTask(task.name, scheduled_time, parent_task=task)
                ScheduledTask.add_to_today(new_task)

    @staticmethod
    def update_schedule():
        time_now = datetime.datetime.now()
        midnight_today = time_now.replace(hour=0, minute=0, second=0, microsecond=0)

        if ScheduledTask.last_updated < midnight_today:
            ScheduledTask.set_up_today()


class RepeatScheduledTask(ScheduledTask):
    def __init__(self, name, task_time, parent_task=None):
        super().__init__(name, task_time, parent_task)
        self.on = True
        Alerts.add_to_schedule(self)
        self.complete = False

    def on_toggle(self):
        self.on = not self.on
        if not self.on:
            Alerts.remove_from_schedule(self)
            self.complete = False
        if self.on and not self.complete:
            Alerts.add_to_schedule(self)

    def complete_toggle(self):
        self.complete = not self.complete
        if self.complete:
            Alerts.remove_from_schedule(self)
        if not self.complete and self.on:
            Alerts.add_to_schedule(self)

    def get_task_time(self):
        self._task_time = self._task_time.replace(second=0, microsecond=0)
        return self._task_time

    def set_task_time(self, task_time):
        self._task_time = task_time.replace(second=0, microsecond=0)


class CountdownTimer(ScheduledTask):
    def __init__(self, task_time):
        super().__init__("Countdown Timer", task_time)
