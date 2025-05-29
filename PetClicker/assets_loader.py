import pygame

class AssetsLoader:
    def __init__(self):
        self.dog_images = [
            pygame.image.load("dogs/dog1.png").convert_alpha(),
            pygame.image.load("dogs/dog2.png").convert_alpha(),
            pygame.image.load("dogs/dog3.png").convert_alpha(),
            pygame.image.load("dogs/dog4.png").convert_alpha(),
            pygame.image.load("dogs/dog5.png").convert_alpha(),
            pygame.image.load("dogs/dog6.png").convert_alpha(),
            pygame.image.load("dogs/dog7.png").convert_alpha(),
            pygame.image.load("dogs/dog8.png").convert_alpha(),
            pygame.image.load("dogs/dog9.png").convert_alpha(),
            pygame.image.load("dogs/dog10.png").convert_alpha()
        ]
        self.backgrounds = [
            pygame.image.load("background/background_lvl1.png").convert(),
            pygame.image.load("background/background_lvl2.png").convert(),
            pygame.image.load("background/background_lvl3.png").convert(),
            pygame.image.load("background/background_lvl4.png").convert(),
            pygame.image.load("background/background_lvl5.png").convert(),
            pygame.image.load("background/background_lvl6.png").convert(),
            pygame.image.load("background/background_lvl7.png").convert(),
            pygame.image.load("background/background_lvl8.png").convert(),
            pygame.image.load("background/background_lvl9.png").convert(),
            pygame.image.load("background/background_lvl10.png").convert(),
            pygame.image.load("background/background_lvl11.png").convert()

        ]
        self.frame = pygame.image.load("frame.png").convert_alpha()

