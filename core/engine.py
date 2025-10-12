from core import context, event_handler, scene_manager
from scenes import splash, menu, level
from systems import discord

from settings import *

import pygame

class Game:
    def __init__(self) -> None:
        context.GameContext.set_game(self)

        self.scene_manager = scene_manager.SceneManager()
    
    def handle_events(self):
        return self.scene_manager.active.handle_events()

    def update(self): 
        self.scene_manager.update()
    def draw(self):
        self.scene_manager.draw()
    
    def run(self):
        
        self.discordrpc = discord.DiscordRPC()
        
        pygame.init()
        
        window = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.OPENGL | pygame.DOUBLEBUF
        )
        self.window = pygame.Surface(window.get_size(), pygame.SRCALPHA, 32)
        pygame.display.set_caption("Break Out V2")

        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()

        self.splash_scene = splash.SplashScene()
        self.menu_scene = menu.MenuScene()
        self.level_scene = level.LevelScene()

        self.active_scene = self.scene_manager.set_active_scene(self.splash_scene if not DEBUG_DISABLE_SPLASH else self.menu_scene)

        while True:
            if not self.handle_events():
                break
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(TARGET_FPS)

        pygame.quit()