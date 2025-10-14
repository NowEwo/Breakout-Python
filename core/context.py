class GameContext:
    _game = None

    @classmethod
    def set_game(cls, game):
        cls._game = game

    @classmethod
    def get_game(cls):
        return cls._game


class Context:
    def __init__(self) -> None:
        self.game = GameContext.get_game()
        assert type(self.game) is not None
