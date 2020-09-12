import os
import signal
import time
import datetime

from reminders.events import Buttons, Clock, Alerts
from reminders.menu import HomeMenu, ActionItem, ListMenu, Menu, TaskMenu
from reminders.screen import Screen
from reminders.tasks import NamedTask


def power_off():
    # requires keyboard input
    # print("\nSelect y to really poweroff, or n to just exit program")
    # off = ""
    # while off != "y":
    #     off = input("do you want to poweroff? y/n > ")
    #     if off == "n":
    #         exit()
    Screen.off()
    time.sleep(0.5)
    os.system("sudo shutdown now")
    exit()


def exit_program():
    Screen.off()
    exit()


# example of a menu with sub-menus and actions
def setup_menu():
    def carrot():
        Screen.text_screen("carrot")
        os.system("play /home/pi/reminder_pi/assets/sounds/beam_sound.wav &")
        time.sleep(3)

    carrot = ActionItem("carrot", carrot)
    pea = ActionItem("pea", lambda: print("here is a pea"))
    cod = ActionItem("cod", lambda: print("here is a cod"))
    parrot = ActionItem("parrot", lambda: print("here is a parrot"))
    robin = ActionItem("robin", lambda: print("here is a robin"))
    sheep = ActionItem("sheep", lambda: print("here is a sheep"))
    cow = ActionItem("cow", lambda: print("here is a cow"))

    shutdown = ActionItem("shutdown", power_off)
    exit_item = ActionItem("exit", exit_program)

    mammal = ListMenu("mammal",
                      [cow, sheep, TaskMenu(NamedTask("My Task", datetime.datetime.now() + datetime.timedelta(20)))])
    bird = ListMenu("bird", [robin, parrot])
    animal = ListMenu("animal", [mammal, bird, cod])
    vegetable = ListMenu("vegetable", [pea, carrot])

    top_level = ListMenu("main_menu", [animal, vegetable, exit_item, shutdown])
    Menu.initialise(HomeMenu(top_level))


# handles a button press and updates screen
def button_handler(button):
    Menu.current().handle_button_press(button)
    Menu.current().display()


def clock_handler():
    Menu.current().handle_time()


if __name__ == '__main__':
    setup_menu()
    Buttons.setup_buttons(button_handler)
    Clock.set_up_clock(clock_handler)
    Menu.current().display()
    # Alerts.add_to_schedule(NamedTask("test task", datetime.datetime.now() + datetime.timedelta(seconds=10)))
    Alerts.set_up_alerts()
    signal.pause()
