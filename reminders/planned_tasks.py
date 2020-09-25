import datetime
import json

from reminders.data import DataIO


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
    def load_tasks():
        tasks_from_file = DataIO.read_in_repeat_tasks()
        for task in tasks_from_file:
            hour, minute = task["time"].split()[0:2]
            RepeatTask.tasks.append(RepeatTask(task["name"], datetime.time(int(hour), int(minute)), task["days"]))
