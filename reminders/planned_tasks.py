import datetime

from reminders.events import Alerts
from reminders.scheduled_tasks import Task


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
        midnight = time_now - datetime.timedelta(hours=time_now.hour, minutes=time_now.minute, seconds=time_now.second,
                                                 microseconds=time_now.microsecond)
        if Alerts.last_updated < midnight:
            for task in RepeatTask.tasks:
                if task.task_days[datetime.datetime.now().weekday()]:
                    scheduled_time = midnight + datetime.timedelta(hours=task.task_time.hour,
                                                                   minutes=task.task_time.minute)
                    Alerts.add_to_schedule(Task(task.name, scheduled_time))

        Alerts.last_updated = time_now
