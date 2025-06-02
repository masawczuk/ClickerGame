import pygame
from .click_upgrade import ClickUpgrade
from .ps_upgrade import PSUpgrade
from .temp_multiplier import TemporaryMultiplierUpgrade

class UpgradeManager:
    def __init__(self):
        self.dog_upgrade_score = 0  # liczba ulepszeń do zmiany psa
        self.background_upgrade_score = 0  # liczba ulepszeń do zmiany planszy

        self.dog_thresholds = [5, 15, 25, 35, 40, 50, 70, 90, 140, 160]
        self.background_thresholds = [10, 20, 30, 45, 65, 80, 110, 130, 155, 180, 200]

        click1 = ClickUpgrade(cost=10, add_points=1)
        click1.on_upgrade()

        self.click_upgrades = [
            click1,
            ClickUpgrade(cost=50, add_points=5),
            ClickUpgrade(cost=100, add_points=10)
        ]

        # Punkty na sekundę
        self.ps_upgrades = [
            PSUpgrade(cost=100, add_points=1),   # +1 pkt/s
            PSUpgrade(cost=500, add_points=5),   # +5 pkt/s
            PSUpgrade(cost=1000, add_points=10)  # +10 pkt/s
        ]

        # Czasowe mnożniki razy 2 (5s, 10s, 15s)
        self.temp_multipliers = [
            TemporaryMultiplierUpgrade(cost=200, duration_ms=5000),
            TemporaryMultiplierUpgrade(cost=600, duration_ms=10000),
            TemporaryMultiplierUpgrade(cost=1200, duration_ms=15000)
        ]

        self.points_per_click_multiplier = 1
        self.temp_multiplier_active = False
        self.temp_multiplier_end_time = 0

    def total_points_per_click(self):
        base = sum(upgrade.get_points() for upgrade in self.click_upgrades)
        base += 1  # dodaj stały bonus startowy
        multiplier = self.get_active_multiplier()
        return base * multiplier

    def get_active_multiplier(self):
        if self.temp_multiplier_active and pygame.time.get_ticks() < self.temp_multiplier_end_time:
            return self.points_per_click_multiplier * 2
        else:
            self.temp_multiplier_active = False
            return self.points_per_click_multiplier

    def activate_temporary_multiplier(self, duration_ms):
        self.temp_multiplier_active = True
        self.temp_multiplier_end_time = pygame.time.get_ticks() + duration_ms

    def total_points_per_second(self):
        return sum(upgrade.get_points() for upgrade in self.ps_upgrades)

    # Funkcje do wykonywania ulepszeń
    def perform_click_upgrade(self, idx, current_points):
        if 0 <= idx < len(self.click_upgrades):
            current_points, success = self.click_upgrades[idx].perform_upgrade(current_points)
            if success:
                self._handle_upgrade_success()
            return current_points, success
        return current_points, False

    def perform_ps_upgrade(self, idx, current_points):
        if 0 <= idx < len(self.ps_upgrades):
            current_points, success = self.ps_upgrades[idx].perform_upgrade(current_points)
            if success:
                self._handle_upgrade_success()
            return current_points, success
        return current_points, False

    def perform_temp_multiplier_upgrade(self, idx, current_points):
        if 0 <= idx < len(self.temp_multipliers):
            current_points, success = self.temp_multipliers[idx].perform_upgrade(current_points, self)
            if success:
                self._handle_upgrade_success()
            return current_points, success
        return current_points, False

    def _handle_upgrade_success(self):
        # Każde ulepszenie zwiększa liczniki do zmiany psa i tła
        self.dog_upgrade_score += 1
        self.background_upgrade_score += 1

        # Sprawdź progi psa
        for threshold in self.dog_thresholds:
            if self.dog_upgrade_score == threshold:
                self.dog_change_needed = True
                break

        # Sprawdź progi tła
        for threshold in self.background_thresholds:
            if self.background_upgrade_score == threshold:
                self.background_change_needed = True
                break