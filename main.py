import pygame, sys
from debug import debug
from level import Level
from settings import *

# 다음의 링크를 보고 따라 작성함.
# https://www.youtube.com/watch?v=QU1pPzEGrqw

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Zilda")
        self.level = Level()

        # sound
        main_sound = pygame.mixer.Sound('./audio/main.ogg')
        main_sound.set_volume(0.08)
        main_sound.play(loops = -1)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level.toggle_menu()

            self.screen.fill(WATER_COLOR)
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()
