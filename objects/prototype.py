# type: ignore

from core.context import GameContext


class Entity(GameContext):
    def __init__(self) -> None:
        self.game = GameContext.get_game()
        self.scene = self.game.active_scene

    def update(self):
        return

    def draw(self):
        return
