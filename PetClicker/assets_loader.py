import pygame

class AssetsLoader:
    def __init__(self):
        self.dog_images = [
            pygame.image.load(f"dogs/dog{i}.png").convert_alpha()
            for i in range(1, 11)
        ]

        self.backgrounds = [
            pygame.image.load(f"background/background_lvl{i}.png").convert()
            for i in range(1, 12)
        ]

        self.frame = pygame.image.load("frame.png").convert_alpha()

