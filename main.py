from systems.logging import Logger
from core.engine import Game

def main():
    Logger("main").highlight("Welcome to BrokeOut")
    Game().run()


if __name__ == "__main__":
    main()
