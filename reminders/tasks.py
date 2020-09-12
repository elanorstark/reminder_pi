class Task:
    def __init__(self, name):
        self.name = name


class NamedTask(Task):
    def __init__(self, name):
        super().__init__(name)


class CountdownTimer(Task):
    def __init__(self):
        super().__init__("Countdown Timer")