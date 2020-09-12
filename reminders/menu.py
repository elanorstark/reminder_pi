from datetime import datetime

from typing import List

from reminders.events import Clock
from reminders.screen import Screen


class ListMenuItem:
    def __init__(self, name):
        self.name = str(name)

    def selected(self):
        pass


# an item in a menu that does something other than going to another menu
class ActionItem(ListMenuItem):
    def __init__(self, name, action):
        super().__init__(name)
        self.action = action

    def selected(self):
        self.action()


class Menu(ListMenuItem):
    menu_stack = []

    def __init__(self, name):
        super().__init__(name)

    def display(self):
        Screen.text_screen(self.name + "\n" + "-" * len(self.name))

    # decides what to do depending on which button was pressed
    # a = select, b = up menu, y = down menu, x = home screen
    def handle_button_press(self, button):
        pass

    def handle_time(self):
        pass

    # returns current menu, ie top of stack
    @staticmethod
    def current():
        return Menu.menu_stack[-1]

    # adds the top level menu to the stack
    @staticmethod
    def initialise(menu):
        Menu.menu_stack = [menu]

    # when back button is pressed - go back to previous level of menu
    @staticmethod
    def back():
        if len(Menu.menu_stack) > 1:
            Menu.menu_stack.pop()


class ListMenu(Menu):

    # initialise a MenuList
    def __init__(self, name: str, items: List[ListMenuItem]):
        super().__init__(name)
        self.items: List[ListMenuItem] = [ActionItem("..", Menu.back)] + items
        self.position = 0

    # decides what to do depending on which button was pressed
    # a = select, b = up menu, y = down menu, x = home screen
    def handle_button_press(self, button):
        if button == "a":
            # select
            self.items[self.position].selected()
        elif button == "b":
            # up
            self.position -= 1
            self.position %= len(self.items)
        elif button == "y":
            # down
            self.position += 1
            self.position %= len(self.items)
        elif button == "x":
            # home/toplevel button
            Menu.menu_stack = Menu.menu_stack[:1]

    # displays menu on screen
    def display(self):
        text = self.name + "\n" + ("-" * len(self.name)) + "\n"
        for i, item in enumerate(self.items):
            if i == self.position:
                text += "A -> {}\n".format(item.name)
            else:
                text += "     {}\n".format(item.name)
        print(text)
        Screen.text_screen(text)

    # adds menu to the stack when selected
    def selected(self):
        Menu.menu_stack.append(self)
        self.position = 0


# for the highest level of menus - doesn't allow going back past here
class HomeMenu(Menu):

    def __init__(self, main_menu):
        super().__init__("Home")
        self.main_menu = main_menu
        self.clock = Clock()

    def handle_time(self):
        self.display()

    def handle_button_press(self, button):
        if button == "a":
            # go to main menu
            Menu.menu_stack.append(self.main_menu)
        elif button == "b":
            # check original design
            pass
        elif button == "y":
            # check original design
            pass
        elif button == "x":
            Menu.menu_stack.append(BacklightOffMenu())

    def display(self):
        now = datetime.now()
        Screen.text_screen(self.name + "\n\n" + now.strftime("%H:%M") + "\n" + now.strftime("%d/%m"))


class TaskMenu(Menu):

    def __init__(self, name):
        super().__init__(name)


class TimeMenu(Menu):

    def __init__(self, name: str):
        super().__init__(name)
        self.time = None

    def display(self):
        Screen.text_screen(self.name + "\n")


class BacklightOffMenu(Menu):
    def __init__(self):
        super().__init__("Backlight")

    def display(self):
        Screen.off()

    def handle_button_press(self, button):
        if button == "x":
            Menu.menu_stack.pop()
            Screen.toggle_backlight()
