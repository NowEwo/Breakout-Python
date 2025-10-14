# core/scene_manager.py
# type: ignore

import pygame
import importlib
from core import context
from settings import TARGET_FPS
from systems import logging
import sys


class SceneManager(context.Context):
    def __init__(self) -> None:
        self.logger = logging.Logger("core.scene_manager")
        self.active = Scene()  # Empty placeholder scene
        self.scene_cache = {}  # Cache optionnel pour recharger plus vite
        super().__init__()

    def set_active_scene(self, scene_name: str, use_cache: bool = True):
        """Charge et active une scène par son nom"""
        self.logger.log(f"Changing active scene to '{scene_name}'")

        self.active.inactive()
        if hasattr(self.active, "__module__"):
            module_name = self.active.__module__
            if module_name in sys.modules:
                del sys.modules[module_name]

        if use_cache and scene_name in self.scene_cache:
            self.active = self.scene_cache[scene_name]
            self.logger.log(f"Loaded '{scene_name}' from cache")
        else:
            module_name = f"scenes.{scene_name}"

            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                self.logger.error(f"Failed to import scene '{scene_name}': {e}")
                raise

            last_segment = scene_name.split(".")[-1]

            class_name = "".join(part.capitalize() for part in last_segment.split("_")) + "Scene"

            try:
                SceneClass = getattr(module, class_name)
            except AttributeError:
                raise AttributeError(f"The scene '{scene_name}' does not contain a '{class_name}' class.")

            scene = SceneClass()
            self.scene_cache[scene_name] = scene
            self.active = scene
            self.logger.success(f"Loaded new scene '{scene_name}'")

        self.game.active_scene = self.active
        self.active._name = scene_name
        self.active.run()
        return self.active

    def handle_events(self):
        return self.active.handle_events()

    def update(self):
        self.active._runtime_timer += 1
        self.active.update()

    def draw(self):
        self.active.draw()


class Scene(context.Context):
    """Classe de base pour toutes les scènes"""
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

    def inactive(self):
        self.logger.log(f"Scene {self} now inactive")
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self._runtime_timer = 0

    def _get_ticks(self):
        return self._runtime_timer

    def update(self):
        pass

    def draw(self):
        pass


class EntityCollection:
    """Gestion simplifiée d'entités dans une scène"""
    def __init__(self) -> None:
        self._entities = []

    def register_entity(self, entity):
        self._entities.append(entity)
        return entity

    def remove_entity(self, entity):
        if entity in self._entities:
            self._entities.remove(entity)
            del entity

    def update(self):
        for entity in self._entities:
            entity.update()

    def draw(self):
        for entity in self._entities:
            entity.draw()