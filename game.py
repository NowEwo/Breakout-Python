# -*- coding: utf-8 -*-
# (c) 2025 Ewo , Titwix , Eliot Hartel

from components.error_handler import ErrorHandler
from components.audio import AudioEngine
from components.logging import Logger
from components.shaders import ShaderEngine
from settings import (RENDER_HEIGHT, RENDER_WIDTH,
                      WINDOW_HEIGHT, WINDOW_WIDTH,
                      FONT_SIZE,
                      TARGET_FPS,
                      DEV_MODE,
                      VERSION)

import random
import sys

import pygame
import pygame.freetype

from entities.ball import Ball
from entities.brick import Brick
from entities.player import Player

from effects.screen_shake import ScreenShake

from components.discord_rpc import DiscordRPC

error_handler = ErrorHandler()

discord_rich_precense = DiscordRPC()
discord_rich_precense.set_rich_presence(1)

class Game:
    """Main game class"""
    
    def __init__(self):

        self.logger = Logger("game")
        self.logger.highlight("Welcome to Break Out")

        if(DEV_MODE):
            self.logger.warn("You're running the game in developpement mode, expect developpement features and some bugs")

        # Initialize Pygame game window
        pygame.init()
        pygame.freetype.init()
        
        # Setup display constants and mode
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.render_width = RENDER_WIDTH
        self.render_height = RENDER_HEIGHT
        
        pygame.display.set_mode(
            (self.width, self.height),
            pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
        )
        self.screen = pygame.Surface((self.render_width, self.render_height))
        pygame.mouse.set_visible(False)
        
        # Load icon (Useless on Wayland but anyway why not)
        icon = pygame.image.load("assets/images/Icon.png")
        pygame.display.set_icon(icon)

        self.shaders_engine = ShaderEngine(self)
        
        # Audio
        self.audio_engine = AudioEngine()

        # Load the main font
        self.font = pygame.freetype.Font("assets/fonts/pixelated.ttf", FONT_SIZE)
        
        # Game state and actual initialisation stuff
        self.bounds = {
            'x_min': 0,
            'y_min': 0,
            'x_max': self.render_width,
            'y_max': self.render_height
        }
        
        self.primary_color = (255, 153, 191)
        self.background_color = [c // 3 for c in self.primary_color]
        
        self.player = Player(self.bounds)
        self.ball = Ball(400, 400)
        self.bricks = []
        self.generate_bricks()
        
        self.screen_shake = ScreenShake()
        self.clock = pygame.time.Clock()
        
        self.started = False
        self.level = 1
        self.hint_text = "Click to start game"
        self.timers = {"Hint": 120}
        self.displayed_score = 0

        self.autoplay = False
        self.fast = False
        
        self.shaders_engine.set_curvature(0)

        self.update_window_title()
    
    def update_window_title(self):
        pygame.display.set_caption(f"Broken out (ALPHA) v{VERSION} • Level {self.level} "+("[AUTOPLAY] " if self.autoplay else "")+("[x5]" if self.fast else ""))
    
    def generate_bricks(self):
        """Generate brick layout"""
        self.bricks = []
        for i in range(9):
            for j in range(14):
                brick = Brick(
                    50 + (j * 53),
                    59 + (i * 33),
                    self.primary_color
                )
                self.bricks.append(brick)
        
        self.logger.success("Created a 9*14 brick grid")
    
    def show_hint(self, text, duration=60):
        """Display a hint message (Subtitle-like)"""
        self.timers["Hint"] = duration
        self.hint_text = text
    
    def handle_events(self):
        """Process events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.logger.critical("Requested game exit")
                self.logger.success("Have a nice day :3")
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.ball.on_player:
                    self.ball.on_player = False
                    self.ball.set_velocity_by_angle(60)
                    
                    if not self.started:
                        self.audio_engine.set_volume(1)
                        self.level = 1
                        self.show_hint("Level 1")
                        self.started = True
                        self.audio_engine.start_music()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    state = self.audio_engine.toggle()
                    self.show_hint("Music "+("ON" if state else "OFF"))
                
                elif event.key == pygame.K_d and DEV_MODE:
                    self.bricks = []
                
                elif event.key == pygame.K_f and DEV_MODE:
                    self.audio_engine.move(51)
                
                elif event.key == pygame.K_SPACE and DEV_MODE:
                    self.fast = not self.fast
                    self.update_window_title()

                elif event.key == pygame.K_a:
                    self.autoplay = not self.autoplay
                    self.show_hint("Autoplay "+("ON" if self.autoplay else "OFF"))
                    self.update_window_title()
            
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.size
                pygame.display.set_mode(
                    (self.width, self.height),
                    pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
                )
                self.shaders_engine.ctx.viewport = (0, 0, self.width, self.height)
        
        return True
    
    def update(self):
        """Update game state (every frames)"""
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x = mouse_x * self.render_width / self.width
        
        # Update player position
        if(not self.autoplay):
            self.player.move(mouse_x)
        else:
            self.player.move(self.ball.x)
        
        # Move ball and check if game is lost
        result = self.ball.move(self.player, self.bounds, self.autoplay)
        if result == 'lost':
            if self.player.lives != 1:
                self.player.lives -= 1
                self.logger.log(f"Player lose this round, now having {self.player.lives} more lives")
            else:
                self.logger.log("Player lose the game, resetting all states")
                self.reset_game()
            self.ball.on_player = True
        
        # Update volume (with some easing because why not)
        self.audio_engine.update_volume()
        
        # Check for level completion (Yea I know that's the crappiest way possible of doing that but anyways)
        if len(self.bricks) == 0:
            self.screen_shake.start(duration=30, magnitude=5)
            self.level += 1 if self.started else 1

            self.logger.log(f"All bricks are broken, now going to level {self.level}")

            self.update_window_title()
            discord_rich_precense.set_rich_presence(self.level)
            
            if self.started:
                self.show_hint(f"Level {self.level}")
            
            # Generate new colors
            self.primary_color = tuple(random.randint(100, 255) for _ in range(3))
            self.background_color = [c // 3 for c in self.primary_color]
            self.logger.success(f"Generated new colors : {self.primary_color=} {self.background_color=}")
            
            self.generate_bricks()

            self.player.lives += 1
            self.logger.log(f"Player won this round, now having {self.player.lives} lives")
        
        # Check brick collisions and do some fancy effect if there's one
        for brick in self.bricks:
            if brick.is_alive():
                score_change = brick.check_ball_collision(self.ball)
                if score_change is not None:
                    self.logger.log(f"Requested score update : {self.player.score}{'+' if score_change >= 0 else ''}{score_change}={self.player.score+score_change}")
                    self.screen_shake.start(duration=3, magnitude=3)
                    hint = ("" if score_change < 0 else "+") + str(score_change)
                    self.show_hint(hint)
                    self.player.score += score_change
                    self.shaders_engine.set_curvature(0.41)
                    self.bricks.remove(brick)
    
    def reset_game(self):
        """Reset game to initial state"""
        self.bricks = []

        self.level = 1
        self.started = False
        self.player.lives = 2
        self.player.score = -1
        self.shaders_engine.set_curvature(0)
        self.audio_engine.set_volume(0.1)
        self.show_hint("You lose")

        discord_rich_precense.set_rich_presence(1)
    
    def draw(self):
        """Render a frame"""
        offset_x, offset_y = self.screen_shake.get_offset()
        
        # Clear the screen
        self.screen.fill(self.background_color)
        
        # Draw game objects
        self.ball.draw(
            self.screen,
            self.primary_color,
            self.background_color,
            offset_x,
            offset_y,
            self.started
        )
        self.player.draw(self.screen, self.primary_color, offset_x, offset_y)
        
        for brick in self.bricks:
            if brick.is_alive():
                brick.draw(self.screen, offset_x, offset_y)
            else:
                self.bricks.remove(brick)
        
        # Draw GUI
        score_text = f'score: {self.displayed_score} | Lifes: {self.player.lives}'
        self.font.render_to(
            self.screen,
            (31 + offset_x, 13 + offset_y),
            score_text,
            self.primary_color
        )
        
        self.font.render_to(
            self.screen,
            (self.render_width - 251 + offset_x, 13 + offset_y),
            'Broken out',
            self.primary_color
        )
        
        # Animate score (interpolation)
        if self.displayed_score < self.player.score:
            diff = (self.player.score - self.displayed_score) // 2
            self.displayed_score += max(1, diff)
        elif self.displayed_score > self.player.score:
            diff = (self.displayed_score - self.player.score) // 2
            self.displayed_score -= max(1, diff)
        
        # Update timers (-1 per frames)
        if self.started:
            for key in self.timers:
                if self.timers[key] > 0:
                    self.timers[key] -= 1
        
        # Draw the hint
        if self.timers["Hint"] > 0:
            hint_x = self.bounds['x_max'] // 2 - ((len(self.hint_text) // 2) * 24)
            hint_y = self.bounds['y_max'] - 91
            alpha = self.timers["Hint"] % 2000
            hint_color = (
                self.primary_color[0],
                self.primary_color[1],
                self.primary_color[2],
                alpha
            )
            self.font.render_to(
                self.screen,
                (hint_x + offset_x, hint_y + offset_y),
                self.hint_text,
                hint_color
            )
        

        self.shaders_engine.render_frame()
        
        pygame.display.flip()
        self.clock.tick(TARGET_FPS if not self.fast else TARGET_FPS*5)
    
    def run(self):
        """Main loop"""
        while True:
            if not self.handle_events():
                break
            self.update()
            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
