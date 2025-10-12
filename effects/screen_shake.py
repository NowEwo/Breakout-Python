from systems.logging import Logger
from settings import (SHAKE_DURATION,
                      SHAKE_MAGNITUDE)

from core.context import Context

import random

class ScreenShake(Context):
    """Manages screen shake effects"""
    def __init__(self):
        self.logger = Logger("effects.screen_shake")

        self.offset = [0, 0]
        self.duration = 0
        self.magnitude = SHAKE_MAGNITUDE
        super().__init__()
    
    def start(self, duration=SHAKE_DURATION, magnitude=SHAKE_MAGNITUDE):
        """Start a screen shake effect"""
        self.logger.log(f"Screen shake triggered with {duration=} frames and {magnitude=}")
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