# -*- coding: utf-8 -*-

import math
import random
import sys

import moderngl
import numpy as np
import pygame
import pygame.freetype

from settings import (SHAKE_DURATION,
                      SHAKE_MAGNITUDE,
                      RENDER_HEIGHT,
                      RENDER_WIDTH,
                      BALL_RADIUS,
                      TRAIL_LENGTH,
                      PLAYER_WIDTH_MULTIPLIER,
                      INITIAL_LIVES,
                      FONT_SIZE,
                      WINDOW_HEIGHT,
                      WINDOW_WIDTH,
                      TARGET_FPS)

# Discord rich presence
import discordrpc
from discordrpc.utils import timestamp

DISCORD_APPLICATION_ID = 1425483708424650772
rpc = discordrpc.RPC(app_id=DISCORD_APPLICATION_ID)

START_TIMESTAMP = timestamp
rpc.set_activity(
      state="Level 1",
      details="Playing with bricks",
      ts_start=START_TIMESTAMP
)


class ScreenShake:
    """Manages screen shake effects"""
    
    def __init__(self):
        self.offset = [0, 0]
        self.duration = 0
        self.magnitude = SHAKE_MAGNITUDE
    
    def start(self, duration=SHAKE_DURATION, magnitude=SHAKE_MAGNITUDE):
        """Start a screen shake effect"""
        self.duration = duration
        self.magnitude = magnitude
    
    def get_offset(self):
        """Get current shake offset and update duration"""
        if self.duration > 0:
            self.offset[0] = random.randint(-self.magnitude, self.magnitude)
            self.offset[1] = random.randint(-self.magnitude, self.magnitude)
            self.duration -= 1
        else:
            self.offset[0] = 0
            self.offset[1] = 0
        return tuple(self.offset)


class Ball:
    """Ball object that also manages the trail"""
    
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 8
        self.vx = 0
        self.vy = 0
        self.on_player = True
        self.trail = []
        self.set_velocity_by_angle(60)
    
    def set_velocity_by_angle(self, angle):
        """Set ball velocity based on angle"""
        self.vx = self.speed * math.cos(math.radians(angle))
        self.vy = -self.speed * math.sin(math.radians(angle))
    
    def draw(self, surface, primary_color, background_color, offset_x=0, offset_y=0, game_started=False):
        """Draw ball and trail"""
        current_pos = (int(self.x - BALL_RADIUS + offset_x), 
                      int(self.y - BALL_RADIUS + offset_y))
        self.trail.insert(0, current_pos)
        
        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop()
        
        # Draw trail with gradient effect generated from numpy (What did I do that ? -Ewo)
        gradient = np.linspace(background_color, primary_color, num=TRAIL_LENGTH, dtype=int)
        if game_started:
            for i, pos in enumerate(reversed(self.trail)):
                pygame.draw.circle(surface, gradient[i], pos, BALL_RADIUS, 0)
        
        # Draw actual ball
        pygame.draw.circle(surface, primary_color, current_pos, BALL_RADIUS, 0)
    
    def bounce_off_player(self, player):
        """Calculate bounce angle based on player hit x"""
        diff = player.x - self.x
        total_length = player.width / 2 + BALL_RADIUS
        angle = 90 + 80 * diff / total_length
        self.set_velocity_by_angle(angle)
    
    def move(self, player, bounds):
        """Update ball position and handle collisions"""
        if self.on_player:
            self.y = player.y - 1.5 * BALL_RADIUS
            self.x = player.x + BALL_RADIUS
        else:
            self.x += self.vx
            self.y += self.vy
            
            # Player collision
            if player.collides_with_ball(self) and self.vy > 0:
                self.bounce_off_player(player)
            
            # Wall collisions
            if (self.x + BALL_RADIUS > bounds['x_max'] or 
                self.x - BALL_RADIUS < bounds['x_min']):
                self.vx = -self.vx
            
            # Lose the game (Bottom)
            if self.y + BALL_RADIUS > bounds['y_max']:
                return 'lost'
            
            # Top
            if self.y - BALL_RADIUS < bounds['y_min']:
                self.vy = -self.vy
        
        return None


class Player:
    """Player-controlled player"""
    
    def __init__(self, bounds):
        self.x = (bounds['x_min'] + bounds['x_max']) / 2
        self.y = bounds['y_max'] - BALL_RADIUS - 5
        self.width = PLAYER_WIDTH_MULTIPLIER * BALL_RADIUS
        self.lives = INITIAL_LIVES
        self.score = 0
        self.bounds = bounds
    
    def draw(self, surface, color, offset_x=0, offset_y=0):
        """Draw the player rect"""
        rect = pygame.Rect(
            int(self.x - self.width / 2 + offset_x),
            int(self.y - BALL_RADIUS + offset_y),
            self.width,
            2 * BALL_RADIUS
        )
        pygame.draw.rect(surface, color, rect, 0)
    
    def move(self, x):
        """Move player to x position (Check for the position not to be outbounds)"""
        if x - self.width / 2 < self.bounds['x_min']:
            self.x = self.bounds['x_min'] + self.width / 2
        elif x + self.width / 2 > self.bounds['x_max']:
            self.x = self.bounds['x_max'] - self.width / 2
        else:
            self.x = x
    
    def collides_with_ball(self, ball):
        """Check collision with ball"""
        vertical = abs(self.y - ball.y) < 2 * BALL_RADIUS
        horizontal = abs(self.x - ball.x) < self.width / 2 + BALL_RADIUS
        return vertical and horizontal


class Brick:
    """Brick object, That's, Ewww, A Brick"""
    
    def __init__(self, x, y, primary_color):
        self.x = x
        self.y = y
        self.life = 1
        self.width = 50
        self.height = 30
        
        # Random color variation
        divisor = random.randint(2, 5)
        self.color = [c // (divisor // 2) for c in primary_color]
    
    def is_alive(self):
        """Check if brick is still alive (This was a trial, I'm making a note here: Huge success)"""
        return self.life > 0
    
    def draw(self, surface, offset_x=0, offset_y=0):
        """Draw the brick"""
        rect = pygame.Rect(
            int(self.x - self.width / 2 + offset_x),
            int(self.y - self.height / 2 + offset_y),
            self.width,
            self.height
        )
        pygame.draw.rect(surface, self.color, rect, 0)
    
    def check_ball_collision(self, ball):
        """Check and handle collision with ball"""
        margin = self.height / 2 + BALL_RADIUS
        dy = ball.y - self.y
        hit = False
        
        if ball.x >= self.x:
            dx = ball.x - (self.x + self.width / 2 - self.height / 2)
            if abs(dy) <= margin and dx <= margin:
                hit = True
                if dx <= abs(dy):
                    ball.vy = -ball.vy
                else:
                    ball.vx = -ball.vx
        else:
            dx = ball.x - (self.x - self.width / 2 + self.height / 2)
            if abs(dy) <= margin and -dx <= margin:
                hit = True
                if -dx <= abs(dy):
                    ball.vy = -ball.vy
                else:
                    ball.vx = -ball.vx
        
        if hit:
            self.life = -1
            score_change = int(25 * dy)
            return score_change
        
        return None


class Game:
    """Main game class"""
    
    def __init__(self):
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
        pygame.display.set_caption("Broken out - v0.1.5")
        
        # Load icon (Useless on Wayland but anyway why not)
        icon = pygame.image.load("assets/images/Icon.png")
        pygame.display.set_icon(icon)
        
        # Setup OpenGL context
        self.ctx = moderngl.create_context()
        self.setup_shaders()
        
        # Audio
        pygame.mixer.init()
        pygame.mixer.music.load("assets/audio/BackgroundMusic.opus")
        self.current_volume = 1.0
        self.requested_volume = 1.0
        
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
        
        self.prog["warp"].value = 0
    
    def setup_shaders(self):
        """Initialize OpenGL shaders"""
        with open("shaders/crt.glsl") as f:
            frag_shader_src = f.read()
        
        vertex_shader_src = """
        #version 120
        attribute vec2 in_vert;
        varying vec2 v_text;
        void main() {
            v_text = (in_vert + 1.0) / 2.0;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
        """
        
        self.prog = self.ctx.program(
            vertex_shader=vertex_shader_src,
            fragment_shader=frag_shader_src
        )
        
        vertices = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype="f4")
        
        vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, "in_vert")
        
        self.texture = self.ctx.texture((self.width, self.height), 3)
        self.texture.repeat_x = False
        self.texture.repeat_y = False
    
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
    
    def show_hint(self, text, duration=60):
        """Display a hint message (Subtitle-like)"""
        self.timers["Hint"] = duration
        self.hint_text = text
    
    def handle_events(self):
        """Process events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.ball.on_player:
                    self.ball.on_player = False
                    self.ball.set_velocity_by_angle(60)
                    
                    if not self.started:
                        self.requested_volume = 1
                        self.level = 1
                        self.show_hint("Level 1")
                        self.started = True
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.play(-1)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                        self.show_hint("Music OFF")
                    else:
                        pygame.mixer.music.play(-1)
                        self.show_hint("Music ON")
                
                elif event.key == pygame.K_d:
                    self.bricks = []
                
                elif event.key == pygame.K_f:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.set_pos(51)
            
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.size
                pygame.display.set_mode(
                    (self.width, self.height),
                    pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
                )
                self.ctx.viewport = (0, 0, self.width, self.height)
        
        return True
    
    def update(self):
        """Update game state (every frames)"""
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x = mouse_x * self.render_width / self.width
        
        # Update player position
        self.player.move(mouse_x)
        
        # Move ball and check if game is lost
        result = self.ball.move(self.player, self.bounds)
        if result == 'lost':
            if self.player.lives != 1:
                self.player.lives -= 1
            else:
                self.reset_game()
            self.ball.on_player = True
        
        # Update volume (with some easing because why not)
        if self.current_volume < self.requested_volume:
            self.current_volume += 0.01
            pygame.mixer.music.set_volume(self.current_volume)
        elif self.current_volume > self.requested_volume:
            self.current_volume -= 0.01
            pygame.mixer.music.set_volume(self.current_volume)
        
        # Check for level completion (Yea I know that's the crappiest way possible of doing that but anyways)
        if len(self.bricks) == 0:
            self.screen_shake.start(duration=30, magnitude=5)
            self.level += 1 if self.started else 1

            rpc.set_activity(
                state=f"Level {self.level}",
                details="Playing with bricks",
                ts_start=START_TIMESTAMP
            )
            
            if self.started:
                self.show_hint(f"Level {self.level}")
            
            # Generate new colors
            self.primary_color = tuple(random.randint(100, 255) for _ in range(3))
            self.background_color = [c // 3 for c in self.primary_color]
            
            self.generate_bricks()
            self.player.lives += 1
        
        # Check brick collisions and do some fancy effect if there's one
        for brick in self.bricks:
            if brick.is_alive():
                score_change = brick.check_ball_collision(self.ball)
                if score_change is not None:
                    self.screen_shake.start(duration=3, magnitude=3)
                    hint = ("" if score_change < 0 else "+") + str(score_change)
                    self.show_hint(hint)
                    self.player.score += score_change
                    self.prog["warp"].value = 0.41
                    self.bricks.remove(brick)
    
    def reset_game(self):
        """Reset game to initial state"""
        self.bricks = []

        self.level = 1
        self.started = False
        self.player.lives = 2
        self.player.score = -1
        self.prog["warp"].value = 0
        self.requested_volume = 0.1
        self.show_hint("You lose")

        rpc.set_activity(
            state="Level 1",
            details="Playing with bricks",
            ts_start=START_TIMESTAMP
        )
    
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
        
        # Apply shader (Don't take care about the IDE errors)
        flipped = pygame.transform.flip(self.screen, False, True)
        texture_data = pygame.image.tostring(flipped, "RGB")
        self.texture.write(texture_data)
        self.texture.use(0)
        
        self.prog["iResolution"].value = (self.width, self.height)
        if self.started and self.prog["warp"].value < 0.5:
            self.prog["warp"].value += 0.01
        self.prog["scan"].value = 0.1
        self.prog["iChannel0"].value = 0
        
        self.ctx.clear(0.0, 0.0, 0.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)
        
        pygame.display.flip()
        self.clock.tick(TARGET_FPS)
    
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
