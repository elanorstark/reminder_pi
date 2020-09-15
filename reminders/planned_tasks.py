import datetime
import json

from reminders.events import Alerts
from reminders.scheduled_tasks import NamedTask


class RepeatTask:
    tasks = []
    task_days = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

    def __init__(self, name, time, days):
        self.name = name
        self.task_time = time
        self.task_days = days

    def add_days(self, days):
        for day in days:
            self.task_days[day] = True

    def remove_days(self, days):
        for day in days:
            self.task_days[day] = False

    @staticmethod
    def add_task(name, time, days):
        RepeatTask.tasks.append(RepeatTask(name, time, days))

    @staticmethod
    def delete_task(task):
        RepeatTask.tasks.remove(task)

    @staticmethod
    def set_up_schedule():
        time_now = datetime.datetime.now()
        midnight_today = time_now.replace(hour=0, minute=0, second=0, microsecond=0)

        if Alerts.last_updated < midnight_today:
            for task in RepeatTask.tasks:
                if task.task_days[midnight_today.weekday()]:
                    scheduled_time = midnight_today.replace(hour=task.task_time.hour, minute=task.task_time.minute)
                    Alerts.add_to_schedule(NamedTask(task.name, scheduled_time, parent_task=task))

        Alerts.last_updated = time_now

    @staticmethod
    def load_tasks():
        with open("data/example.json") as json_file:
            test = json.load(json_file)
        for task in test["tasks"]:
            hour, minute = task["time"].split()[0:2]
            RepeatTask.tasks.append(RepeatTask(task["name"], datetime.time(int(hour), int(minute)), task["days"]))
