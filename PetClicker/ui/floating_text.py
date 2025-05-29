import pygame

WHITE = (255, 255, 255)

class FloatingText:
    def __init__(self, x, y, text, color=WHITE):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.alpha = 255
        self.lifetime = 1000  # ms
        self.start_time = pygame.time.get_ticks()

    def update(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        self.y -= 0.5  # unosi się do góry
        self.alpha = max(0, 255 - int((elapsed / self.lifetime) * 255))
        return self.alpha > 0

    def draw(self, screen, font):
        text_surf = font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        screen.blit(text_surf, (self.x, self.y))