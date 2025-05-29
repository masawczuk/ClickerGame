import pygame

class Dog:
    def __init__(self, assets):
        self.assets = assets
        self.shrink_start_time = None
        self.shrink_duration = 500  # ms
        self.shrink_scale_factor = 0.90

    def get_level(self, upgrade_manager):
        thresholds = upgrade_manager.dog_thresholds
        upgrades = upgrade_manager.dog_upgrade_score
        level = 0
        for t in thresholds:
            if upgrades >= t:
                level += 1
            else:
                break
        return min(level, len(self.assets.dog_images) - 1)

    def get_image(self, upgrade_manager):
        return self.assets.dog_images[self.get_level(upgrade_manager)]

    def draw(self, screen, width, height, upgrade_manager):
        scale = min(width / 800, height / 600)
        scale = max(0.5, min(scale, 1.2))

        # Zmniejszenie po kliknięciu
        if self.shrink_start_time:
            elapsed = pygame.time.get_ticks() - self.shrink_start_time
            if elapsed < self.shrink_duration:
                shrink_progress = elapsed / self.shrink_duration
                shrink_amount = 1 - (1 - self.shrink_scale_factor) * (1 - shrink_progress)
                scale *= shrink_amount
            else:
                self.shrink_start_time = None  # reset po animacji

        size = int(300 * scale)
        img = pygame.transform.smoothscale(self.get_image(upgrade_manager), (size, size))

        usable_width = int(width * 0.7)
        x = (usable_width - size) // 2
        y = (height - size) // 2
        screen.blit(img, (x, y))
        return pygame.Rect(x, y, size, size)

    def trigger_shrink(self):
        self.shrink_start_time = pygame.time.get_ticks()