import sys

from systems.logging import Logger
from core.context import GameContext

class ErrorHandler(GameContext):
    def __init__(self) -> None:
        self.logger = Logger("components.error_handler")

        sys.excepthook = self._error_handler

        self.logger.success("Registered global error handler")

    def _error_handler(self, exctype, value, traceback):
        if exctype is KeyboardInterrupt:
            self.logger.log("Keyboard Interrupt triggered, exiting...")
            self.logger.success("Have a nice day :3")
        else:
           self.logger.critical("Error occured D: , now displaying execution dump")
           self.logger.highlight("--------- START OF DUMP ---------")
           for key, value in GameContext.get_game().__dict__.items():
                if(not key.startswith("__")):
                    self.logger.log(f"{key}: {type(value).__name__} = {value}")
           self.logger.highlight("--------- END OF DUMP ---------")
           self.logger.critical(f"Error of type {exctype.__name__} at context [{value}]")
           # sys.__excepthook__(exctype, value, traceback)