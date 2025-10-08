import sys

from components.logging import Logger

class ErrorHandler:
    def __init__(self) -> None:
        self.logger = Logger("components.error_handler")

        sys.excepthook = self._error_handler

        self.logger.success("Registered global error handler")

    def _error_handler(self, exctype, value, traceback):
        if exctype is KeyboardInterrupt:
            self.logger.log("Keyboard Interrupt triggered, exiting...")
            self.logger.success("Have a nice day :3")
        else:
           self.logger.critical(f"Error of type {exctype.__name__} : {value}")
           # sys.__excepthook__(exctype, value, traceback)