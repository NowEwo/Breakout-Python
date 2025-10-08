import random
from settings import (BALL_RADIUS,
                      TRAIL_LENGTH)

import numpy as np
import pygame
import math

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
    
    def move(self, player, bounds, autoplay=False):
        """Update ball position and handle collisions"""
        if self.on_player:
            self.y = player.y - 1.5 * BALL_RADIUS
            self.x = player.x + BALL_RADIUS
        else:
            self.x += self.vx
            self.y += self.vy
            
            # Player collision
            if player.collides_with_ball(self) and self.vy > 0:
                if(not autoplay):
                    self.bounce_off_player(player)
                else:
                    self.vx = self.speed * math.cos(math.radians(random.randint(0,180)))
                    self.vy = -self.vy
            
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