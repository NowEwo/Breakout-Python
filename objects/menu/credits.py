# type: ignore

import pygame
import pygame.freetype

from objects.prototype import Entity
from settings import VERSION, RELEASE_STATE


class Credits(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.font = pygame.freetype.Font("assets/fonts/pixelated.ttf", 24)
        self.text = [
            "Broke Out - By Broke Team (2025)",
            f"Version {VERSION} ({RELEASE_STATE})",
            "",
            "***Developpement Team***",
            "Ewo", "Titouan Brebion-Coïa", "Eliot Hartel",
            "",
            "***Music***", "Ewo on FL Studio",
            "",
            "***Design***",
            "Logo : Ewo",
            "Color palette : Titouan Brebion-Coïa, Eliot Hartel",
            "Easter egg fox : YamikoCrystalYC",
            "",
            "***Gameplay***",
            "Titouan Brebion-Coïa", "Eliot Hartel",
            "",
            "***Special thanks to***",
            "Cantine, Rémi, Sube, Python, UV, Pygame",
            "And that random guy's website solving a bug in a magic way"
            "",
            "Made with love by Broke Team", "<3"
        ]

    # noinspection PyMethodOverriding
    def draw(self, scene):

        if scene.egg:
            image = pygame.image.load("assets/images/credits/egg.png")
            scene.surface.blit(image, (scene.surface.get_rect().center[0] - 213,
                                       scene.scroll + scene.surface.get_rect().center[1] - 175))
            line = "Surprise :3"
            text_rect = self.font.get_rect(line, size=35)
            text_rect.center = (scene.surface.get_rect().center[0],
                                scene.scroll + scene.surface.get_rect().center[1] + 256)
            self.font.render_to(scene.surface, text_rect, line, (0, 0, 0), size=35)
        else:
            i = 0
            for line in self.text:
                i += 1
                text_rect = self.font.get_rect(line, size=24)
                text_rect.center = (scene.surface.get_rect().center[0],
                                    scene.scroll + scene.surface.get_rect().center[1] // 2 + (i * 25))
                self.font.render_to(scene.surface, text_rect, line, self.scene.color, size=24)
