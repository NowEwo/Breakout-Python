import pygame.mixer
from systems.logging import Logger

class AudioEngine:
    def __init__(self) -> None:
        self.logger = Logger("systems.audio")

        pygame.mixer.init()
        self.current_volume = 1.0
        self.requested_volume = 1.0

        self.logger.success(f"New AudioEngine initialised : {self}")
    
    def play_file(self, file, loop=False):
        pygame.mixer.music.load(file)
        if not pygame.mixer.music.get_busy():
            self.logger.log(f"Playing audio file {file} with {loop=}")
            pygame.mixer.music.play(-1 if loop else 0)
        else:
            self.logger.error("AudioEngine busy, cannot play music file")
    
    def set_volume(self, volume):
        self.logger.log("Volume change requested : "+volume)
        self.requested_volume = volume

    def toggle(self, loop=False):
        self.logger.log("Toggling music state")
        if self.state():
            pygame.mixer.music.stop()
        else:
            pygame.mixer.music.play(-1 if loop else 0)
        
        return self.state()

    def stop(self):
        self.logger.log("Stopping music")
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        else:
            self.logger.error("Music not playing, cannot stop")


    def play(self, loop=False):
        self.logger.log("Playing loaded music")
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1 if loop else 0)
        else:
            self.logger.warn("AudioEngine busy, stopping the current music")
            pygame.mixer.music.stop()

    def move(self, pos):
        self.logger.log(f"Moving music time to {pos}")
        if self.state():
            pygame.mixer.music.set_pos(pos)
    
    def update(self):
        if self.current_volume < self.requested_volume:
            self.current_volume += 0.01
            pygame.mixer.music.set_volume(self.current_volume)
        elif self.current_volume > self.requested_volume:
            self.current_volume -= 0.01
            pygame.mixer.music.set_volume(self.current_volume)

    def state(self) -> bool:
        return pygame.mixer.music.get_busy()