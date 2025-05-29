import pygame

class Background:
    def __init__(self, assets):
        self.assets = assets

    def get_level(self, upgrade_manager):
        thresholds = upgrade_manager.background_thresholds
        upgrades = upgrade_manager.background_upgrade_score
        level = 0
        for t in thresholds:
            if upgrades >= t:
                level += 1
            else:
                break
        return min(level, len(self.assets.backgrounds) - 1)

    def draw(self, screen, width, height, upgrade_manager):
        bg = pygame.transform.scale(self.assets.backgrounds[self.get_level(upgrade_manager)], (width, height))
        screen.blit(bg, (0, 0))