import pygame.mixer

class AudioEngine:
    def __init__(self) -> None:
        pygame.mixer.init()
        self.current_volume = 1.0
        self.requested_volume = 1.0
    
    def play_file(self, file, loop=False):
        pygame.mixer.music.load(file)
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1 if loop else 0)
    
    def set_volume(self, volume):
        self.requested_volume = volume

    def toggle(self, loop=False):
        if self.state():
            pygame.mixer.music.stop()
        else:
            pygame.mixer.music.play(-1 if loop else 0)
        
        return self.state()

    def stop(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()


    def play(self, loop=False):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1 if loop else 0)

    def move(self, pos):
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