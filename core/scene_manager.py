#type: ignore

from core import context

from settings import TARGET_FPS

import pygame

class SceneManager(context.Context):
    def __init__(self) -> None:
        self.active = Scene() # Set an empty scene as the active one

        super().__init__()

    def set_active_scene(self, scene):
        self.active.inactive()
        self.game.active_scene = scene
        self.active = scene
        self.active.run()

    def handle_events(self):
        return self.active.handle_events()

    def update(self):
        self.active._runtime_timer += 1
        self.active.update()

    def draw(self):
        self.active.draw()

class Scene(context.Context):
    def __init__(self) -> None:
        super().__init__()
        self._entities = []
        self._runtime_timer = 0.0
    
    def register_entity(self, entity):
        self._entities.append(entity)
        return entity

    def remove_entity(self, entity):
        self._entities.remove(entity)
        del entity
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def run(self):
        return
    
    def inactive(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self._runtime_timer = 0
        return

    def _get_ticks(self):
        return self._runtime_timer

    def update(self):
        return
    
    def draw(self):
        return

# Not finished
class EntityCollection():
    def __init__(self) -> None:
        self._entities = []
    
    def register_entity(self, entity):
        self._entities.append(entity)
        return entity

    def remove_entity(self, entity):
        self._entities.remove(entity)
        del entity

    def update(self):
        for entity in self._entities:
            entity.update()

    def draw(self):
        for entity in self._entities:
            entity.draw()
    