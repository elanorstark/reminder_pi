import datetime

from typing import List

from reminders.screen import Screen


class ListMenuItem:
    def __init__(self, name):
        self._name = str(name)

    @property
    def name(self):
        return self._name

    def set_name(self, name):
        self._name = str(name)

    def selected(self):
        pass


# an item in a menu that does something other than going to another menu
class ActionItem(ListMenuItem):
    def __init__(self, name, action):
        super().__init__(name)
        self.action = action

    def selected(self):
        self.action()


class ToggleableItem(ActionItem):
    def __init__(self, name, is_selected, toggle, pad_width=9):
        super().__init__(name.ljust(pad_width), toggle)
        self.is_selected = is_selected

    @property
    def name(self):
        return self._name + ("[×]" if self.is_selected() else "[ ]")


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
    def __init__(self, name: str, items):
        super().__init__(name)
        self.unevaluated = items
        self.items: List[ListMenuItem] = [ActionItem("..", Menu.back)]
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
    def display(self, title=None):
        if not title:
            title = self.name

        self.items = [ActionItem("..", Menu.back)] + self.unevaluated()
        self.position = min(len(self.items) - 1, self.position)

        text = ""
        for i, item in enumerate(self.items):
            if i == self.position:
                text += "> {}\n".format(item.name)
            else:
                text += "  {}\n".format(item.name)
        print(title, "\n", text)
        Screen.menu_screen(title, text)

    # adds menu to the stack when selected
    def selected(self):
        Menu.menu_stack.append(self)
        self.position = 0


# for the highest level of menus - doesn't allow going back past here
class HomeMenu(Menu):

    def __init__(self, main_menu):
        super().__init__("Home")
        self.main_menu = main_menu

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
        now = datetime.datetime.now()
        Screen.home_screen(self.name, now.strftime("%H:%M"), now.strftime("%a %d %b"))


class TaskMenu(ListMenu):

    def __init__(self, task):
        self.task = task
        super().__init__(self.task.name, self.task_options)

    def display(self, title=None):
        title = "Edit " + self.name
        super(TaskMenu, self).display(title)

    def task_options(self):
        options = [
            TimeMenu(self.task.task_time.strftime("Time     %H:%M")),
            ToggleableItem("On", lambda: self.task.on, self.task.on_toggle)
        ]
        if self.task.on:
            options.append(ToggleableItem("Complete", lambda: self.task.complete, self.task.complete_toggle))
        return options


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


class AlertMenu(Menu):
    def __init__(self, task):
        super().__init__(task.name)
        self.task = task
        self.delayed_for = 0
        self.delay_period = datetime.timedelta(seconds=10)

    def display(self):
        if self.delayed_for > 0:
            Screen.multi_line_text([[self.name, 1], ["Delaying until:", 0], [self.task.task_time.strftime("%H:%M"), 1],
                                    [" ", 0], ["Delayed for", 0], [str(self.delayed_for * self.delay_period), 0]])
        else:
            Screen.multi_line_text([[self.name, 1], ["Alert time:", 0], [self.task.task_time.strftime("%H:%M"), 1]])

    def handle_button_press(self, button):
        if button == "a":
            Menu.menu_stack.pop()
        elif button == "y":
            self.task.delay(self.delay_period)
            self.delayed_for += 1
            self.display()
        elif button == "b":
            self.task.complete_toggle()
