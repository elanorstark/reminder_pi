from typing import List
from reminders.screen import Screen


# an item in a menu
class MenuItem:
    def __init__(self, name):
        self.name = name

    def selected(self):
        pass


class ActionItem(MenuItem):
    def __init__(self, name, action):
        super().__init__(name)
        self.action = action

    def selected(self):
        self.action()


class MenuList(MenuItem):
    menu_stack = []

    def __init__(self, name: str, items: List[MenuItem]):
        super().__init__(name)
        self.items: List[MenuItem] = [ActionItem("..", MenuList.back)] + items
        self.position = 0

    def selected(self):
        MenuList.menu_stack.append(self)
        self.position = 0

    def display(self):
        text = self.name + "\n" + ("-" * len(self.name)) + "\n"
        for i, item in enumerate(self.items):
            if i == self.position:
                text += "A -> {}\n".format(item.name)
            else:
                text += "     {}\n".format(item.name)
        print(text)
        Screen.text_screen(text)

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
            MenuList.menu_stack = MenuList.menu_stack[:1]

    @staticmethod
    def current():
        return MenuList.menu_stack[-1]

    @staticmethod
    def initialise(menu):
        MenuList.menu_stack = [menu]

    @staticmethod
    def back():
        if len(MenuList.menu_stack) > 1:
            MenuList.menu_stack.pop()
