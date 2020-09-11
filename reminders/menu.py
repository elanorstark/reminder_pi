from typing import List
from reminders.screen import Screen


# an item in a menu - used almost like a template
class MenuItem:
    def __init__(self, name):
        self.name = name

    def selected(self):
        pass


# an item in a menu that does something other than going to another menu
class ActionItem(MenuItem):
    def __init__(self, name, action):
        super().__init__(name)
        self.action = action

    def selected(self):
        self.action()


# an item in a menu that displays another menu when selected
class MenuList(MenuItem):
    menu_stack = []

    # initialise a MenuList
    def __init__(self, name: str, items: List[MenuItem]):
        super().__init__(name)
        self.items: List[MenuItem] = [ActionItem("..", MenuList.back)] + items
        self.position = 0

    # adds menu to the stack when selected
    def selected(self):
        MenuList.menu_stack.append(self)
        self.position = 0

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
            print(len(MenuList.menu_stack) > 1, MenuList.menu_stack)
            if len(MenuList.menu_stack) > 1:
                MenuList.menu_stack = MenuList.menu_stack[:1]
                MenuList.menu_stack[0].position = 0
            else:
                Screen.toggle_backlight()

    # returns current menu, ie top of stack
    @staticmethod
    def current():
        return MenuList.menu_stack[-1]

    # adds the top level menu to the stack
    @staticmethod
    def initialise(menu):
        MenuList.menu_stack = [menu]

    # when back button is pressed - go back to previous level of menu
    @staticmethod
    def back():
        if len(MenuList.menu_stack) > 1:
            MenuList.menu_stack.pop()
