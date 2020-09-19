import os
import signal
import time
import datetime

from reminders.events import Buttons, Clock, Alerts
from reminders.menu import HomeMenu, ActionItem, ListMenu, Menu, TaskMenu
from reminders.planned_tasks import RepeatTask
from reminders.screen import Screen
from reminders.scheduled_tasks import ScheduledTask


def create_log():
    import json
    today_json = [{}]
    log = {"tasks": today_json, "date": [1, 1, 1]}
    with open("data/log.json", "w") as json_file:
        json.dump(log, json_file)


def opening_data():
    RepeatTask.load_tasks()
    ScheduledTask.read_in_today()


def saving_data():
    ScheduledTask.write_out_today()


def power_off():
    saving_data()
    Screen.off()
    time.sleep(0.5)
    os.system("sudo shutdown now")
    exit()


def exit_program():
    saving_data()
    Screen.off()
    exit()


# example of a menu with sub-menus and actions
def setup_menu():
    shutdown = ActionItem("shutdown", power_off)
    exit_item = ActionItem("exit", exit_program)

    def schedule():
        return [TaskMenu(x) for x in ScheduledTask.today]

    schedule_item = ListMenu("Schedule", schedule)

    top_level = ListMenu("Main Menu", lambda: [schedule_item, exit_item, shutdown])
    Menu.initialise(HomeMenu(top_level))


# handles a button press and updates screen
def button_handler(button):
    Menu.current().handle_button_press(button)
    Menu.current().display()


def clock_handler():
    Menu.current().handle_time()
    RepeatTask.set_up_schedule()


if __name__ == '__main__':
    opening_data()
    setup_menu()
    Buttons.setup_buttons(button_handler)
    Menu.current().display()
    # for testing, adds tasks at 00:02 and 00:03 of current day
    # RepeatTask.add_task("test 1",
    #                     datetime.time(0, 2), [True, True, True, True, True, True, True])
    # RepeatTask.add_task("test 2",
    #                     datetime.time(0, 3), [True, True, True, True, True, True, True])
    RepeatTask.set_up_schedule()
    Clock.set_up_clock(clock_handler)
    # Alerts.add_to_schedule(NamedTask("test task", datetime.datetime.now() + datetime.timedelta(seconds=10)))
    Alerts.set_up_alerts()
    signal.pause()
