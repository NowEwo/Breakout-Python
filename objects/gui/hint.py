#type: ignore

from objects.prototype import Entity

from settings import *

class HintElement(Entity):
    def __init__(self) -> None:
        self.timer = 120
        self.hint_text = "Click to start game"
        self.size = 24

        super().__init__()
    
    def update(self):
        self.timer -= 1

    def draw(self):

        if self.timer > 0:
            self.text_rect = self.scene.font.get_rect(self.hint_text, size = self.size)
            self.text_rect.center = (self.scene.surface.get_rect().center[0], RENDER_HEIGHT - 139)

            self.scene.font.render_to(self.scene.surface, self.text_rect, self.hint_text, (255, 153, 191, self.timer), size = self.size)


    def show_hint(self, text, duration=120, size=24):
        """Display a hint message (Subtitle-like)"""
        self.timer = duration
        self.hint_text = text
        self.size = size