from .base_upgrade import Upgrade
#Ulepszenia punktów za kliknięcie
class ClickUpgrade(Upgrade):
    def __init__(self, cost, add_points):
        super().__init__(cost)
        self.add_points = add_points
        self.level = 0

    def on_upgrade(self):
        self.level += 1

    def get_points(self):
        return self.add_points * self.level

    def cost_increase_factor(self):
        return 1.5
