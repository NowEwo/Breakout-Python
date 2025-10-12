#type: ignore

from core import context

from systems import logging

from settings import TARGET_FPS

import pygame

class SceneManager(context.Context):
    def __init__(self) -> None:
        self.logger = logging.Logger("core.scene_manager")
        self.active = Scene() # Set an empty scene as the active one

        super().__init__()

    def set_active_scene(self, scene):
        self.logger.log(f"changing active scene to {type(scene)}")
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
        self.logger = logging.Logger("core.scene_manager.scene")
        self._runtime_timer = 0.0
        super().__init__()
        self.logger.success(f"New scene loaded as {self}")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def run(self):
        self.logger.log(f"Scene {self} now running")
        return
    
    def inactive(self):
        self.logger.log(f"Scene {self} now inactive")
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
    