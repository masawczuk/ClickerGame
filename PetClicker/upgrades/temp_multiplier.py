from .base_upgrade import Upgrade

# Czasowy mnożnik punktów za kliknięcie
class TemporaryMultiplierUpgrade(Upgrade):
    def __init__(self, cost, duration_ms):
        super().__init__(cost)
        self.duration_ms = duration_ms
        self.active_until = 0
        self.base_cost = cost


    def on_upgrade(self):
        pass  # Do niczego w tej metodzie

    def activate(self, upgrade_manager):
        upgrade_manager.activate_temporary_multiplier(self.duration_ms)

    def perform_upgrade(self, current_points, upgrade_manager=None):
        if self.can_upgrade(current_points):
            current_points -= self.cost
            self.activate(upgrade_manager)
            self.cost = int(self.cost * 3)
            return current_points, True
        return current_points, False