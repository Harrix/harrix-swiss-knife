import harrix_pylib as h

from harrix_swiss_knife import action_base, fitness

config = h.dev.load_config("config/config.json")


class OnFitness(action_base.ActionBase):
    icon = "🏃🏻"
    title = "Fitness tracker"

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.parent = kwargs.get("parent")
        self.main_window = None

    def execute(self, *args, **kwargs) -> None:
        if self.main_window is None:
            self.main_window = fitness.MainWindow()
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
