import os
import signal

from reminders.buttons import Buttons
from reminders.menu import MenuList, ActionItem


def power_off():
    # requires keyboard input
    print("\nSelect y to really poweroff, or n to just exit program")
    off = ""
    while off != "y":
        off = input("do you want to poweroff? y/n > ")
        if off == "n":
            exit()

    os.system("sudo shutdown now")
    exit()


def setup_menu():
    carrot = ActionItem("carrot", lambda: print("here is a carrot"))
    pea = ActionItem("pea", lambda: print("here is a pea"))
    cod = ActionItem("cod", lambda: print("here is a cod"))
    parrot = ActionItem("parrot", lambda: print("here is a parrot"))
    robin = ActionItem("robin", lambda: print("here is a robin"))
    sheep = ActionItem("sheep", lambda: print("here is a sheep"))
    cow = ActionItem("cow", lambda: print("here is a cow"))

    shutdown = ActionItem("shutdown", power_off)

    mammal = MenuList("mammal", [cow, sheep])
    bird = MenuList("bird", [robin, parrot])
    animal = MenuList("animal", [mammal, bird, cod])
    vegetable = MenuList("vegetable", [pea, carrot])

    top_level = MenuList("main_menu", [animal, vegetable, shutdown])
    MenuList.initialise(top_level)


def button_handler(button):
    MenuList.current().handle_button_press(button)
    MenuList.current().display()


if __name__ == '__main__':
    setup_menu()
    Buttons.setup_buttons(button_handler)
    MenuList.current().display()
    signal.pause()
