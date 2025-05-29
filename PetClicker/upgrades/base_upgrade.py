# Bazowa klasa ulepszenia
class Upgrade:
    def __init__(self, cost):
        self.cost = cost
        self.base_cost = cost  # Dodaj to!

    def can_upgrade(self, current_points):
        return current_points >= self.cost

    def perform_upgrade(self, current_points):
        if self.can_upgrade(current_points):
            current_points -= self.cost
            self.on_upgrade()
            self.cost = int(self.cost * self.cost_increase_factor())
            return current_points, True
        return current_points, False

    def on_upgrade(self):
        pass

    def cost_increase_factor(self):
        return 1.5
