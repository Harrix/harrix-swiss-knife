import harrix_pylib as h

from harrix_swiss_knife import action_base_in_thread, fitness

config = h.dev.load_config("config/config.json")


class on_fitness(action_base_in_thread.ActionBaseInThread):
    icon: str = "🏃🏻"
    title: str = "Fitness tracker"

    def __init__(self, **kwargs):
        self.parent = kwargs.get("parent", None)
        self.main_window = None

    def execute(self, *args, **kwargs):
        if self.main_window is None:
            self.main_window = fitness.MainWindow()
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
