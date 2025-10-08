from settings import (BALL_RADIUS,
                      PLAYER_WIDTH_MULTIPLIER,
                      INITIAL_LIVES)

import pygame

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