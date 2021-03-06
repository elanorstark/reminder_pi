import datetime

from typing import List

from reminders.events import Buttons, Alerts
from reminders.screen import Screen


# highest level, things that can be in a list menu
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


# an action item that is displayed on a menu with a checkbox
class ToggleableItem(ActionItem):
    def __init__(self, name, is_selected, toggle, pad_width=9):
        super().__init__(name.ljust(pad_width), toggle)
        self.is_selected = is_selected

    @property
    def name(self):
        return self._name + ("[×]" if self.is_selected() else "[ ]")


# parent for menus that can be displayed as their own screen
class Menu(ListMenuItem):
    menu_stack = []

    def __init__(self, name):
        super().__init__(name)

    def display(self):
        Screen.text_screen(self.name + "\n" + "-" * len(self.name))

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


# menu for the home screen
# no back button available
class HomeMenu(Menu):
    translation = Buttons.home_menu_buttons

    def __init__(self, main_menu):
        super().__init__("Home")
        self.main_menu = main_menu

    def handle_time(self):
        self.display()

    def handle_button_press(self, button):
        button = HomeMenu.translation[button]

        if button == "home":
            # go to main menu
            Menu.menu_stack.append(self.main_menu)
        elif button == "backlight":
            Menu.menu_stack.append(BacklightOffMenu())

    def display(self):
        now = datetime.datetime.now()
        Screen.home_screen(self.name, now.strftime("%H:%M"), now.strftime("%a %d %b"))


# menu that stores and displays a list of ListMenuItem
class ListMenu(Menu):
    translation = Buttons.list_menu_buttons

    # initialise a MenuList
    def __init__(self, name: str, items):
        super().__init__(name)
        self.unevaluated = items
        self.items: List[ListMenuItem] = [ActionItem("..", Menu.back)]
        self.position = 0

    # decides what to do depending on which button was pressed
    # a = select, b = up menu, y = down menu, x = home screen
    def handle_button_press(self, button):
        button = ListMenu.translation[button]

        if button == "select":
            # select
            self.items[self.position].selected()
        elif button == "up":
            # up
            self.position -= 1
            self.position %= len(self.items)
        elif button == "down":
            # down
            self.position += 1
            self.position %= len(self.items)
        elif button == "home":
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


# menu for reaching the task time editing menu, and to edit on and complete
class TaskMenu(ListMenu):

    def __init__(self, task):
        self.task = task
        super().__init__(self.task.name, self.task_options)

    def display(self, title=None):
        title = "Edit " + self.name
        super(TaskMenu, self).display(title)

    def task_options(self):
        options = [
            TimeMenu(self.task),
            ToggleableItem("On", lambda: self.task.on, self.task.on_toggle)
        ]
        if self.task.on:
            options.append(ToggleableItem("Complete", lambda: self.task.complete, self.task.complete_toggle))
        return options


# menu for editing a task's time
class TimeMenu(ListMenu):
    units_stages = [1, 5, 10]
    menu_stages = ["Hours", "Minutes", "Save/Cancel"]
    translation = Buttons.time_menu_buttons

    def __init__(self, task):
        super().__init__(task.get_task_time().strftime("Time     %H:%M"), lambda: [])
        self.task = task
        self.time = task.get_task_time()
        self.menu_stage = 0
        self.units_stage = 0

    def display(self, title="Edit Time"):
        Screen.multi_line_text(
            [Screen.TextLine(title, 1),
             Screen.TextLine("Unit change: {}".format(TimeMenu.units_stages[self.units_stage]), 0),
             Screen.TextLine(self.time.strftime("%H:%M"), 2, align="c"),
             Screen.TextLine(TimeMenu.menu_stages[self.menu_stage], 1, align="c")])

    def change_task_time(self):
        self.menu_stage = 0
        self.task.set_task_time(self.task.get_task_time().replace(hour=self.time.hour, minute=self.time.minute))
        self.set_name(self.time.strftime("Time     %H:%M"))
        Alerts.sort_alerts()

    def hour_change(self, difference):
        self.time = self.time.replace(hour=(self.time.hour + difference) % 24)

    def minute_change(self, difference):
        self.time = self.time.replace(minute=(self.time.minute + difference) % 60)

    def handle_button_press(self, button):
        button = TimeMenu.translation[button]

        if button == "next":
            self.menu_stage += 1
            self.menu_stage %= len(TimeMenu.menu_stages)
        if button == "decrease":
            if TimeMenu.menu_stages[self.menu_stage] == "Hours":
                self.hour_change(-1)
            elif TimeMenu.menu_stages[self.menu_stage] == "Minutes":
                self.minute_change(0 - TimeMenu.units_stages[self.units_stage])
            elif TimeMenu.menu_stages[self.menu_stage] == "Save/Cancel":
                self.change_task_time()
                super().handle_button_press("a")
        if button == "units":
            self.units_stage += 1
            self.units_stage %= len(TimeMenu.units_stages)
        if button == "increase":
            if TimeMenu.menu_stages[self.menu_stage] == "Hours":
                self.hour_change(1)
            elif TimeMenu.menu_stages[self.menu_stage] == "Minutes":
                self.minute_change(TimeMenu.units_stages[self.units_stage])
            elif TimeMenu.menu_stages[self.menu_stage] == "Save/Cancel":
                super().handle_button_press("a")

    def selected(self):
        super().selected()
        self.menu_stage = 0
        self.units_stage = 0


# menu which is put at top of stack when backlight is turned off
class BacklightOffMenu(Menu):
    def __init__(self):
        super().__init__("Backlight")

    def display(self):
        Screen.off()

    def handle_button_press(self, button):
        if button == "x":
            Menu.menu_stack.pop()
            Screen.toggle_backlight()


# menu to display alert and delay or mark complete
class AlertMenu(Menu):
    translation = Buttons.alert_menu_buttons

    def __init__(self, task, delay=datetime.timedelta(minutes=1)):
        super().__init__(task.name)
        self.task = task
        self.delayed_for = 0
        self.delay_period = delay

    def display(self):
        if self.delayed_for > 0:
            Screen.multi_line_text(
                [Screen.TextLine(self.name, 1), Screen.TextLine("Delaying until:", 0, uniform_y=True),
                 Screen.TextLine(self.task.get_task_time().strftime("%H:%M"), 1),
                 Screen.TextLine(" ", 0), Screen.TextLine("Delayed for", 0),
                 Screen.TextLine(str(self.delayed_for * self.delay_period), 0)])
        else:
            Screen.multi_line_text(
                [Screen.TextLine(self.name, 1), Screen.TextLine("Alert time:", 0, uniform_y=True),
                 Screen.TextLine(self.task.get_task_time().strftime("%H:%M"), 1)])

    def handle_button_press(self, button):
        button = AlertMenu.translation[button]

        if button == "dismiss":
            Menu.menu_stack.pop()
        elif button == "delay":
            self.task.delay(self.delay_period)
            self.delayed_for += 1
            self.display()
        elif button == "complete":
            self.task.complete_toggle()
