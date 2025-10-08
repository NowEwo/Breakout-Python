from components.logging import Logger
from settings import BALL_RADIUS

import pygame
import random

class Brick:
    """Brick object, That's, Ewww, A Brick"""
    
    def __init__(self, x, y, primary_color):
        self.logger = Logger("entities.brick", False)

        self.x = x
        self.y = y
        self.life = 1
        self.width = 50
        self.height = 30
        
        # Random color variation
        divisor = random.randint(2, 5)
        self.color = [c // (divisor // 2) for c in primary_color]

        # self.logger.log(f"New brick with props [{x=} {y=} {self.width=} {self.height=} {self.life=} {self.color=}] as {self}")
    
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
            self.logger.log(f"Brick {self} got hit")
            self.life = -1
            score_change = int(25 * dy) if int(25 * dy) > 0 else 0
            return score_change
        
        return None