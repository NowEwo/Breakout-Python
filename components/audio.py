import pygame.mixer

from components.logging import Logger

class AudioEngine:
    def __init__(self) -> None:
        self.logger = Logger("components.audio")

        self.logger.success("Loaded music into pygame mixer")
        pygame.mixer.init()
        pygame.mixer.music.load("assets/audio/BackgroundMusic.opus")
        self.current_volume = 1.0
        self.requested_volume = 1.0
    
    def start_music(self):
        self.logger.log("Requested music start")
        if not pygame.mixer.music.get_busy():
            self.logger.log("Music state set to playing")
            pygame.mixer.music.play(-1)
    
    def set_volume(self, volume:float):
        self.logger.log(f"Requested new volume : {volume*100} %")
        self.requested_volume = volume
    
    def update_volume(self):
        if self.current_volume < self.requested_volume:
            self.current_volume += 0.01
            pygame.mixer.music.set_volume(self.current_volume)
        elif self.current_volume > self.requested_volume:
            self.current_volume -= 0.01
            pygame.mixer.music.set_volume(self.current_volume)
    
    def state(self) -> bool:
        return pygame.mixer.music.get_busy()
    
    def toggle(self):
        if self.state():
            self.logger.log("Music state set to stopped")
            pygame.mixer.music.stop()
        else:
            self.logger.log("Music state set to playing")
            pygame.mixer.music.play(-1)
        
        return self.state()

    def move(self, pos):
        if self.state():
            self.logger.log(f"Music position set to {pos} seconds")
            pygame.mixer.music.set_pos(pos)