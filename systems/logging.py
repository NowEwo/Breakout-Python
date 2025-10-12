from datetime import datetime
import colorama

class Logger:
    def __init__(self, name="Logger element", verbose=True) -> None:
        self.name = name
        if(verbose):
            self.log(f"Logger element created for {name} as {self}")
    
    def log(self, message):
        print(f"{colorama.Fore.BLUE}({datetime.now()}) [{self.name}] {message}{colorama.Fore.RESET}")

    def highlight(self, message):
        print(f"{colorama.Back.WHITE}{colorama.Fore.BLACK}({datetime.now()}) [{self.name}] {message}{colorama.Fore.RESET}{colorama.Back.RESET}")

    def warn(self, message):
        print(f"{colorama.Fore.YELLOW}({datetime.now()}) [{self.name}] {message}{colorama.Fore.RESET}")

    def success(self, message):
        print(f"{colorama.Fore.GREEN}({datetime.now()}) [{self.name}] {message}{colorama.Fore.RESET}")

    def error(self, message):
        print(f"{colorama.Fore.RED}({datetime.now()}) [{self.name}] {message}{colorama.Fore.RESET}")

    def critical(self, message):
        print(f"{colorama.Back.RED}({datetime.now()}) [{self.name}] {message}{colorama.Back.RESET}")