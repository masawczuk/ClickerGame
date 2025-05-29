from assets_loader import AssetsLoader
from upgrades.manager import UpgradeManager
from entities.dog import Dog
from entities.background import Background
from ui.ui_manager import UIManager
from ui.floating_text import FloatingText
import pygame
import json
import os
import sys

# Stałe
START_WIDTH, START_HEIGHT = 800, 600
FPS = 60

# Kolory
NAVY = "#2D17E5"
WHITE = (255, 255, 255)
PINK = "#C600E5"
BLACK = (0, 0, 0)


pygame.init()

class Game:
    def __init__(self):
        pygame.display.set_mode((START_WIDTH, START_HEIGHT), pygame.RESIZABLE)  # najpierw okno

        self.assets = AssetsLoader()  # teraz ładujemy obrazy

        self.screen = pygame.display.get_surface()  # pobierz aktywny ekran
        pygame.display.set_caption("Clicker z ulepszeniami")
        self.clock = pygame.time.Clock()

        self.upgrade_manager = UpgradeManager()
        self.dog = Dog(self.assets)
        self.background = Background(self.assets)
        self.ui_manager = UIManager(self.assets)

        self.points = 0
        self.last_ps_update = pygame.time.get_ticks()

        self.floating_texts = []
        self.current_player = "Gracz1"  # domyślny gracz – może być później zmieniony w menu wyboru

        self.load_game()


    def add_points(self, amount):
        self.points += amount

    def handle_click(self, pos):
        dog_rect = self.dog.draw(self.screen, *self.screen.get_size(), self.upgrade_manager)
        if dog_rect.collidepoint(pos):
            points_gained = self.upgrade_manager.total_points_per_click()
            self.points += points_gained
            self.floating_texts.append(FloatingText(pos[0], pos[1], f"+{points_gained}"))
            self.dog.trigger_shrink()
            return True

        # Sprawdź kliknięcia na przyciski panelu 1 (tylko jeśli panel 1 jest widoczny)
        if self.ui_manager.panel1_visible:
            rects = self.ui_manager.draw_right_panel(
                self.screen, *self.screen.get_size(),
                [u.cost for u in self.upgrade_manager.click_upgrades],
                [u.cost for u in self.upgrade_manager.ps_upgrades],
                [u.cost for u in self.upgrade_manager.temp_multipliers]
            )
            for i, rect in enumerate(rects):
                if rect.collidepoint(pos):
                    if i < 3:
                        self.points, ok = self.upgrade_manager.perform_click_upgrade(i, self.points)
                        if ok:
                            self.ui_manager.show_info("Ulepszono kliknięcie!", PINK)
                        else:
                            self.ui_manager.show_info("Brak punktów!", NAVY)
                    elif i < 6:
                        idx = i - 3
                        self.points, ok = self.upgrade_manager.perform_ps_upgrade(idx, self.points)
                        if ok:
                            self.ui_manager.show_info("Ulepszono punkty na sekundę!", PINK)
                        else:
                            self.ui_manager.show_info("Brak punktów!", NAVY)
                    else:
                        idx = i - 6
                        self.points, ok = self.upgrade_manager.perform_temp_multiplier_upgrade(idx, self.points)
                        if ok:
                            self.ui_manager.show_info("Aktywowano mnożnik x2 na kliknięcia!", PINK)
                        else:
                            self.ui_manager.show_info("Brak punktów!", NAVY)
                    return True

        # Kliknięcia poza przyciskami nic nie robią
        return False

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_ps_update >= 1000:
            pps = self.upgrade_manager.total_points_per_second()
            multiplier = self.upgrade_manager.get_active_multiplier()
            self.points += int(pps * multiplier)
            self.last_ps_update = now

        self.floating_texts = [ft for ft in self.floating_texts if ft.update()]

    def run(self):
        running = True
        while running:
            self.screen.fill(BLACK)

            width, height = self.screen.get_size()

            self.background.draw(self.screen, width, height, self.upgrade_manager)
            self.dog.draw(self.screen, width, height, self.upgrade_manager)
            pps = self.upgrade_manager.total_points_per_second()
            self.ui_manager.draw_top_panel(self.screen, width, self.points, pps)

            # Rysuj pływające teksty
            font = pygame.font.SysFont("Arial", 24)
            for ft in self.floating_texts:
                ft.draw(self.screen, font)

            # Rysuj panele — draw_right_panel rysuje oba panele i zwraca przyciski z panelu 1
            rects = self.ui_manager.draw_right_panel(
                self.screen, width, height,
                [u.cost for u in self.upgrade_manager.click_upgrades],
                [u.cost for u in self.upgrade_manager.ps_upgrades],
                [u.cost for u in self.upgrade_manager.temp_multipliers]
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Obsługa toggle przycisków dla paneli
                    if self.ui_manager.toggle_button_rect1.collidepoint(event.pos):
                        self.ui_manager.toggle_panel("panel1", width)
                    elif self.ui_manager.toggle_button_rect2.collidepoint(event.pos):
                        self.ui_manager.toggle_panel("panel2", width)
                    elif self.save_button_rect.collidepoint(event.pos):
                        self.save_game()
                        self.ui_manager.show_info("Gra zapisana!", PINK)
                    elif hasattr(self, "new_game_button_rect") and self.new_game_button_rect.collidepoint(event.pos):
                        self.reset_game()
                        self.ui_manager.show_info("Nowa gra rozpoczęta!", PINK)
                    elif self.load_game_button_rect.collidepoint(event.pos):
                        self.choose_player()
                    else:
                        self.handle_click(event.pos)


            self.update()

            self.save_icon = pygame.image.load("icons/save.png").convert_alpha()
            self.new_game_icon = pygame.image.load("icons/newgame.png").convert_alpha()
            self.load_game_icon = pygame.image.load("icons/user.png").convert_alpha()

            # Dodaj przyciski z ikonami
            #Przycisk zapisu gry
            save_button_radius = 20
            save_button_center = (30, 30)
            self.save_button_rect = pygame.Rect(0, 0, save_button_radius * 2, save_button_radius * 2)
            self.save_button_rect.center = save_button_center
            save_icon_scaled = pygame.transform.smoothscale(self.save_icon,
                                                            (save_button_radius * 2, save_button_radius * 2))
            self.screen.blit(save_icon_scaled,
                             (save_button_center[0] - save_button_radius, save_button_center[1] - save_button_radius))


            #Przycisk nowej gry
            new_game_button_radius = 20
            new_game_button_center = (30, 80)
            self.new_game_button_rect = pygame.Rect(0, 0, new_game_button_radius * 2, new_game_button_radius * 2)
            self.new_game_button_rect.center = new_game_button_center
            new_game_icon_scaled = pygame.transform.smoothscale(self.new_game_icon, (
            new_game_button_radius * 2, new_game_button_radius * 2))
            self.screen.blit(new_game_icon_scaled, (
            new_game_button_center[0] - new_game_button_radius, new_game_button_center[1] - new_game_button_radius))

            #Przycisk załadowania gry
            load_game_button_radius = 20
            load_game_button_center = (30, 130)
            self.load_game_button_rect = pygame.Rect(0, 0, load_game_button_radius * 2, load_game_button_radius * 2)
            self.load_game_button_rect.center = load_game_button_center
            load_game_icon_scaled = pygame.transform.smoothscale(self.load_game_icon, (
            load_game_button_radius * 2, load_game_button_radius * 2))
            self.screen.blit(load_game_icon_scaled, (
            load_game_button_center[0] - load_game_button_radius, load_game_button_center[1] - load_game_button_radius))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def save_game(self):
        if not self.current_player:
            self.ui_manager.show_info("Brak wybranego gracza!", NAVY)
            return

        data = {
            "points": self.points,
            "click_upgrades": [{"level": u.level, "cost": u.cost} for u in self.upgrade_manager.click_upgrades],
            "ps_upgrades": [{"level": u.level, "cost": u.cost} for u in self.upgrade_manager.ps_upgrades],
            "temp_multipliers": [{"active_until": u.active_until, "cost": u.cost} for u in
                                 self.upgrade_manager.temp_multipliers],
            "click_costs": [u.cost for u in self.upgrade_manager.click_upgrades],
            "ps_costs": [u.cost for u in self.upgrade_manager.ps_upgrades],
            "dog_upgrade_score": self.upgrade_manager.dog_upgrade_score,
            "background_upgrade_score": self.upgrade_manager.background_upgrade_score
        }

        save_path = f"save_{self.current_player}.json"
        with open(save_path, "w") as f:
            json.dump(data, f)

        self.ui_manager.show_info(f"Zapisano jako {self.current_player}", PINK)

    def load_game(self):
        if not self.current_player:
            self.ui_manager.show_info("Brak wybranego gracza!", NAVY)
            return

        filename = f"save_{self.current_player}.json"
        if not os.path.exists(filename):
            return  # lub opcjonalnie: self.ui_manager.show_info("Brak zapisu!", NAVY)

        with open(filename, "r") as f:
            data = json.load(f)

        # RESETUJ aktualne wartości przed załadowaniem nowych danych
        for upgrade in self.upgrade_manager.click_upgrades:
            upgrade.level = 0
            upgrade.cost = upgrade.base_cost  # Upewnij się, że masz base_cost!

        for upgrade in self.upgrade_manager.ps_upgrades:
            upgrade.level = 0
            upgrade.cost = upgrade.base_cost

        for upgrade in self.upgrade_manager.temp_multipliers:
            upgrade.cost = upgrade.base_cost
            upgrade.active_until = 0

        self.upgrade_manager.dog_upgrade_score = 0
        self.upgrade_manager.background_upgrade_score = 0

        self.points = data.get("points", 0)
        for i, upgrade_data in enumerate(data.get("click_upgrades", [])):
            self.upgrade_manager.click_upgrades[i].level = upgrade_data.get("level", 0)
            self.upgrade_manager.click_upgrades[i].cost = upgrade_data.get("cost",
                                                                           self.upgrade_manager.click_upgrades[i].cost)

        for i, upgrade_data in enumerate(data.get("ps_upgrades", [])):
            self.upgrade_manager.ps_upgrades[i].level = upgrade_data.get("level", 0)
            self.upgrade_manager.ps_upgrades[i].cost = upgrade_data.get("cost",
                                                                        self.upgrade_manager.ps_upgrades[i].cost)

        for i, multiplier_data in enumerate(data.get("temp_multipliers", [])):
            self.upgrade_manager.temp_multipliers[i].active_until = multiplier_data.get("active_until", 0)
            self.upgrade_manager.temp_multipliers[i].cost = multiplier_data.get("cost",
                                                                                self.upgrade_manager.temp_multipliers[
                                                                                    i].cost)
        for i, lvl in enumerate(data.get("click_levels", [])):
            self.upgrade_manager.click_upgrades[i].level = lvl
        for i, cost in enumerate(data.get("click_costs", [])):
            self.upgrade_manager.click_upgrades[i].cost = cost

        for i, lvl in enumerate(data.get("ps_levels", [])):
            self.upgrade_manager.ps_upgrades[i].level = lvl
        for i, cost in enumerate(data.get("ps_costs", [])):
            self.upgrade_manager.ps_upgrades[i].cost = cost

        # Liczniki zmian psa i tła
        self.upgrade_manager.dog_upgrade_score = data.get("dog_upgrade_score", 0)
        self.upgrade_manager.background_upgrade_score = data.get("background_upgrade_score", 0)
    def reset_game(self):
        self.points = 0
        for upgrade in self.upgrade_manager.click_upgrades:
            upgrade.level = 0
            upgrade.cost = upgrade.base_cost  # Jeśli masz base_cost — jeśli nie, pomiń tę linię

        for upgrade in self.upgrade_manager.ps_upgrades:
            upgrade.level = 0
            upgrade.cost = upgrade.base_cost  # Jeśli masz base_cost

        for upgrade in self.upgrade_manager.temp_multipliers:
            upgrade.cost = upgrade.base_cost  # Jeśli masz base_cost
            if hasattr(upgrade, 'active_until'):
                upgrade.active_until = 0
        self.upgrade_manager.dog_upgrade_score = 0
        self.upgrade_manager.background_upgrade_score = 0

        self.floating_texts = []
        self.ui_manager.show_info("Nowa gra rozpoczęta!", PINK)
        save_path = f"save_{self.current_player}.json"
        if os.path.exists(save_path):
            os.remove(save_path)

    def choose_player(self):
        if not os.path.exists("players.json"):
            with open("players.json", "w") as f:
                json.dump(["Gracz1"], f)

        with open("players.json", "r") as f:
            players = json.load(f)

        if not players:
            players = ["Gracz1"]

        width, height = self.screen.get_size()
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(220)
        overlay.fill((50, 50, 50))

        font = pygame.font.SysFont("Arial", 28)
        running = True
        selected_idx = 0

        while running:
            self.screen.blit(overlay, (0, 0))

            title = font.render("Wybierz gracza:", True, WHITE)
            self.screen.blit(title, (width // 2 - title.get_width() // 2, 100))

            for i, name in enumerate(players):
                color = PINK if i == selected_idx else WHITE
                text = font.render(name, True, color)
                self.screen.blit(text, (width // 2 - text.get_width() // 2, 180 + i * 40))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_idx = (selected_idx - 1) % len(players)
                    elif event.key == pygame.K_DOWN:
                        selected_idx = (selected_idx + 1) % len(players)
                    elif event.key == pygame.K_RETURN:
                        selected_player = players[selected_idx]
                        self.current_player = selected_player
                        self.load_game()
                        self.ui_manager.show_info(f"Wczytano: {selected_player}", PINK)
                        return

    def load_game_for_player(self, player_name):
        filename = f"save_{player_name}.json"
        if not os.path.exists(filename):
            self.ui_manager.show_info("Brak zapisu tego gracza!", NAVY)
            return

        with open(filename, "r") as f:
            data = json.load(f)
        self.points = data.get("points", 0)
        for i, lvl in enumerate(data.get("click_levels", [])):
            self.upgrade_manager.click_upgrades[i].level = lvl
        for i, lvl in enumerate(data.get("ps_levels", [])):
            self.upgrade_manager.ps_upgrades[i].level = lvl
        for i, ts in enumerate(data.get("multiplier_states", [])):
            self.upgrade_manager.temp_multipliers[i].active_until = ts

