import random

import pygame

from objects.prototype import Entity
from settings import BALL_RADIUS
from systems.logging import Logger


class Brick(Entity):
    """Brick object, That's, Ewww, A Brick"""

    def __init__(self, x, y, scene):
        super().__init__()
        self.logger = Logger("objects.brick", False)

        self.x = x
        self.y = y
        self.life = random.randint(1, 3)
        self.text = ""
        self.width = 50
        self.height = 30

        # Random color variation
        divisor = random.randint(2, 5)
        self.scene = scene
        self.color = [c // (divisor // 2) for c in scene.color]

        # self.logger.log(f"New brick with props [{x=} {y=} {self.width=} {self.height=} {self.life=} {self.color=}] as {self}")

    def is_alive(self):
        """Check if brick is still alive (This was a trial, I'm making a note here: Huge success)"""
        return self.life > 0

    def draw(self):
        """Draw the brick"""
        rect = pygame.Rect(
            int(self.x - self.width / 2 + self.scene.offset_x),
            int(self.y - self.height / 2 + self.scene.offset_y),
            self.width,
            self.height
        )
        pygame.draw.rect(self.scene.surface, self.color, rect, 0)

        self.text_rect = self.scene.font.get_rect("•" * self.life, size=16)
        self.text_rect.center = (self.x, self.y)

        self.scene.font.render_to(self.scene.surface, self.text_rect, "•" * self.life, self.scene.background_color(),
                                  size=16)

    def handle_hit(self):
        pass

    def check_ball_collision(self):
        """Check and handle collision with ball"""
        ball = self.scene.ball

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
            self.handle_hit()
            self.logger.log(f"Brick {self} got hit")
            self.life -= 1
            score_change = int(25 * dy) if int(25 * dy) > 0 else 0
            return score_change

        return None


class BrickGroup(Entity):
    def __init__(self) -> None:
        self.logger = Logger("objects.brick.brickgroup")
        self.bricks = []

        super().__init__()

        self.logger.log("Initialised brick group")

    def generate_bricks(self):
        """Generate brick layout"""
        self.bricks = []
        for i in range(9):
            for j in range(14):
                brick = Brick(((i % 2) * 13) + 51 + (j * 53), 59 + (i * 33), self.scene)
                self.bricks.append(brick)

    def update(self):
        if len(self.bricks) == 0:
            self.logger.log(f"All bricks are broken, now going to level {self.scene.level}")

            self.scene.trigger_next_level()

            self.generate_bricks()

        # Check brick collisions and do some fancy effect if there's one
        for brick in self.bricks:
            if brick.is_alive():
                score_change = brick.check_ball_collision()
                if score_change is not None:
                    self.logger.log(
                        f"Requested score update : {self.scene.score}{'+' if score_change >= 0 else ''}{score_change}={self.scene.score + score_change}"
                    )
                    self.scene.screen_shake.start(duration=3, magnitude=3)
                    hint = ("" if score_change < 0 else "+") + str(score_change)
                    self.scene.score += score_change
                    self.scene.shaders.set_curvature(0.41)

    def draw(self):
        for brick in self.bricks:
            if brick.is_alive():
                brick.draw()
            else:
                self.bricks.remove(brick)
