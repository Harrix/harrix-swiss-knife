from PySide6.QtCore import QThread, Signal

class ThreadForAction(QThread):
    """
    Thread class for executing actions.

    Attributes:

    - `finished` (`Signal`): Signal to emit the result.
    - `error` (`Signal`): Signal to emit any errors.
    - `action_method` (`callable`): The method to be executed in the thread.
    - `args` (`tuple`): The positional arguments to pass to the `action_method`.
    - `kwargs` (`dict`): The keyword arguments to pass to the `action_method`.
    """

    finished = Signal(object)
    error = Signal(Exception)

    def __init__(self, action_method, args, kwargs):
        """
        Initializes the ActionThread with a method and its arguments.

        Args:

        - `action_method` (`callable`): The method to be executed in the thread.
        - `args` (`tuple`): The positional arguments for `action_method`.
        - `kwargs` (`dict`): The keyword arguments for `action_method`.
        """
        super().__init__()
        self.action_method = action_method
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """
        Executes the action method with the provided arguments.

        Emits:

        - `finished`: if the action completes successfully, emitting the result.
        - `error`: if an exception occurs, emitting the exception.
        """
        try:
            result = self.action_method(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)