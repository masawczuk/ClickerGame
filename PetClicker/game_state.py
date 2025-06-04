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

START_WIDTH, START_HEIGHT = 800, 600
FPS = 60

NAVY = "#2D17E5"
WHITE = (255, 255, 255)
PINK = "#C600E5"
BLACK = (0, 0, 0)

pygame.init()

class Game:
    def __init__(self):
        pygame.display.set_mode((START_WIDTH, START_HEIGHT), pygame.RESIZABLE)
        self.assets = AssetsLoader()
        self.screen = pygame.display.get_surface()
        pygame.display.set_caption("Pet Clicker")
        self.clock = pygame.time.Clock()

        self.upgrade_manager = UpgradeManager()
        self.dog = Dog(self.assets)
        self.background = Background(self.assets)
        self.ui_manager = UIManager(self.assets)

        self.points = 0
        self.last_ps_update = pygame.time.get_ticks()

        self.save_icon = pygame.image.load("icons/save.png").convert_alpha()
        self.new_game_icon = pygame.image.load("icons/newgame.png").convert_alpha()
        self.load_game_icon = pygame.image.load("icons/user.png").convert_alpha()

        self.floating_texts = []
        self.current_player = "Gracz1"
        if os.path.exists(f"save_{self.current_player}.json"):
            self.load_game()
        else:
            self.reset_game()

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
                        self.ui_manager.show_info("Ulepszono kliknięcie!" if ok else "Brak punktów!", PINK if ok else NAVY)
                    elif i < 6:
                        idx = i - 3
                        self.points, ok = self.upgrade_manager.perform_ps_upgrade(idx, self.points)
                        self.ui_manager.show_info("Ulepszono punkty na sekundę!" if ok else "Brak punktów!", PINK if ok else NAVY)
                    else:
                        idx = i - 6
                        self.points, ok = self.upgrade_manager.perform_temp_multiplier_upgrade(idx, self.points)
                        self.ui_manager.show_info("Aktywowano mnożnik x2" if ok else "Brak punktów!", PINK if ok else NAVY)
                    return True
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
        if not self.current_player:
            self.choose_player()
            if not self.current_player:
                pygame.quit()
                sys.exit()
        running = True
        while running:
            self.screen.fill(BLACK)
            width, height = self.screen.get_size()

            self.background.draw(self.screen, width, height, self.upgrade_manager)
            self.dog.draw(self.screen, width, height, self.upgrade_manager)
            pps = self.upgrade_manager.total_points_per_second()
            self.ui_manager.draw_top_panel(self.screen, width, self.points, pps)

            font = pygame.font.SysFont("Arial", 24)
            for ft in self.floating_texts:
                ft.draw(self.screen, font)

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
                    if self.ui_manager.toggle_button_rect1.collidepoint(event.pos):
                        self.ui_manager.toggle_panel("panel1", width)
                    elif self.ui_manager.toggle_button_rect2.collidepoint(event.pos):
                        self.ui_manager.toggle_panel("panel2", width)
                    elif self.save_button_rect.collidepoint(event.pos):
                        self.save_game()
                    elif self.new_game_button_rect.collidepoint(event.pos):
                        self.reset_game()
                    elif self.load_game_button_rect.collidepoint(event.pos):
                        self.choose_player()
                    else:
                        self.handle_click(event.pos)

            self.update()

            self.save_button_rect = self.draw_icon_button(self.save_icon, (30, 30))
            self.new_game_button_rect = self.draw_icon_button(self.new_game_icon, (30, 80))
            self.load_game_button_rect = self.draw_icon_button(self.load_game_icon, (30, 130))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def draw_icon_button(self, icon, center):
        radius = 20
        rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        rect.center = center
        icon_scaled = pygame.transform.smoothscale(icon, (radius * 2, radius * 2))
        self.screen.blit(icon_scaled, (center[0] - radius, center[1] - radius))
        return rect

    def save_game(self):
        if not self.current_player:
            self.ui_manager.show_info("Brak wybranego gracza!", NAVY)
            return

        data = {
            "points": self.points,
            "click_upgrades": [{"level": u.level, "cost": u.cost} for u in self.upgrade_manager.click_upgrades],
            "ps_upgrades": [{"level": u.level, "cost": u.cost} for u in self.upgrade_manager.ps_upgrades],
            "temp_multipliers": [{"active_until": u.active_until, "cost": u.cost} for u in self.upgrade_manager.temp_multipliers],
            "dog_upgrade_score": self.upgrade_manager.dog_upgrade_score,
            "background_upgrade_score": self.upgrade_manager.background_upgrade_score
        }

        save_path = f"save_{self.current_player}.json"
        try:
            with open(save_path, "w") as f:
                json.dump(data, f)
            self.ui_manager.show_info(f"Zapisano jako {self.current_player}", PINK)
        except Exception as e:
            self.ui_manager.show_info(f"Błąd zapisu: {str(e)}", NAVY)

    def load_game(self):
        if not self.current_player:
            self.ui_manager.show_info("Brak wybranego gracza!", NAVY)
            return

        filename = f"save_{self.current_player}.json"
        if not os.path.exists(filename):
            self.ui_manager.show_info("Brak zapisu dla tego gracza!", NAVY)
            return

        try:
            with open(filename, "r") as f:
                data = json.load(f)
            self._load_game_data(data)
            self.ui_manager.show_info(f"Wczytano: {self.current_player}", PINK)
        except Exception as e:
            self.ui_manager.show_info(f"Błąd wczytywania: {str(e)}", NAVY)

    def reset_game(self):
        self.points = 0
        self.reset_upgrades_to_base()
        self.upgrade_manager.dog_upgrade_score = 0
        self.upgrade_manager.background_upgrade_score = 0
        self.floating_texts = []
        self.ui_manager.show_info("Nowa gra rozpoczęta!", PINK)

        save_path = f"save_{self.current_player}.json"
        if os.path.exists(save_path):
            os.remove(save_path)

    def reset_upgrades_to_base(self):
        for upgrade in self.upgrade_manager.click_upgrades:
            upgrade.level = 0
            upgrade.cost = upgrade.base_cost

        for upgrade in self.upgrade_manager.ps_upgrades:
            upgrade.level = 0
            upgrade.cost = upgrade.base_cost

        for upgrade in self.upgrade_manager.temp_multipliers:
            upgrade.cost = upgrade.base_cost
            upgrade.active_until = 0

    def _load_game_data(self, data):
        self.reset_upgrades_to_base()
        self.points = data.get("points", 0)

        for i, upgrade_data in enumerate(data.get("click_upgrades", [])):
            self.upgrade_manager.click_upgrades[i].level = upgrade_data.get("level", 0)
            self.upgrade_manager.click_upgrades[i].cost = upgrade_data.get("cost", self.upgrade_manager.click_upgrades[i].cost)

        for i, upgrade_data in enumerate(data.get("ps_upgrades", [])):
            self.upgrade_manager.ps_upgrades[i].level = upgrade_data.get("level", 0)
            self.upgrade_manager.ps_upgrades[i].cost = upgrade_data.get("cost", self.upgrade_manager.ps_upgrades[i].cost)

        for i, multiplier_data in enumerate(data.get("temp_multipliers", [])):
            self.upgrade_manager.temp_multipliers[i].active_until = multiplier_data.get("active_until", 0)
            self.upgrade_manager.temp_multipliers[i].cost = multiplier_data.get("cost", self.upgrade_manager.temp_multipliers[i].cost)

        self.upgrade_manager.dog_upgrade_score = data.get("dog_upgrade_score", 0)
        self.upgrade_manager.background_upgrade_score = data.get("background_upgrade_score", 0)

    def choose_player(self):
        players_file = "players.json"

        # Upewnij się, że plik istnieje i zawiera listę
        if not os.path.exists(players_file):
            with open(players_file, "w") as f:
                json.dump([], f)

        try:
            with open(players_file, "r") as f:
                players = json.load(f)
        except Exception:
            players = []

        width, height = self.screen.get_size()
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(220)
        overlay.fill((50, 50, 50))

        font = pygame.font.SysFont("Arial", 28)
        small_font = pygame.font.SysFont("Arial", 24)

        running = True
        selected_idx = 0
        input_mode = len(players) == 0  # automatycznie włącz wpisywanie, jeśli brak graczy
        input_text = ""
        delete_buttons = []

        while running:
            self.screen.blit(overlay, (0, 0))
            delete_buttons = []

            title_text = "Dodaj pierwszego gracza" if len(players) == 0 else "Wybierz gracza / Dodaj / Usuń"
            title = font.render(title_text, True, WHITE)
            self.screen.blit(title, (width // 2 - title.get_width() // 2, 60))

            all_options = players + ["+ Nowy gracz..."]

            for i, name in enumerate(all_options):
                y = 130 + i * 40
                color = PINK if i == selected_idx else WHITE
                text = font.render(name, True, color)
                text_rect = text.get_rect(center=(width // 2, y))
                self.screen.blit(text, text_rect)

                if i < len(players):
                    x_button_rect = pygame.Rect(text_rect.right + 10, y - 10, 30, 30)
                    pygame.draw.rect(self.screen, (200, 50, 50), x_button_rect)
                    x_text = font.render("X", True, WHITE)
                    self.screen.blit(x_text, (x_button_rect.x + 5, x_button_rect.y))
                    delete_buttons.append((x_button_rect, i))
                else:
                    delete_buttons.append((None, None))

            if input_mode:
                prompt = small_font.render("Nowy gracz: " + input_text, True, WHITE)
                self.screen.blit(prompt, (width // 2 - prompt.get_width() // 2, height - 100))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if players:
                        running = False
                        pygame.quit()
                        sys.exit()
                    else:
                        self.ui_manager.show_info("Dodaj przynajmniej jednego gracza!", NAVY)

                elif event.type == pygame.KEYDOWN:
                    if input_mode:
                        if event.key == pygame.K_RETURN:
                            new_player = input_text.strip()
                            if new_player and new_player not in players:
                                players.append(new_player)
                                with open(players_file, "w") as f:
                                    json.dump(players, f)
                                self.current_player = new_player
                                self.reset_game()  # nowy gracz = czysty start
                                return
                            input_mode = False
                            input_text = ""
                        elif event.key == pygame.K_ESCAPE:
                            if len(players) == 0:
                                continue  # nie pozwalaj wyjść bez gracza
                            input_mode = False
                            input_text = ""
                        elif event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        else:
                            if len(input_text) < 16:
                                input_text += event.unicode
                    else:
                        if event.key == pygame.K_UP:
                            selected_idx = (selected_idx - 1) % len(all_options)
                        elif event.key == pygame.K_DOWN:
                            selected_idx = (selected_idx + 1) % len(all_options)
                        elif event.key == pygame.K_RETURN:
                            if selected_idx < len(players):
                                self.current_player = players[selected_idx]
                                if os.path.exists(f"save_{self.current_player}.json"):
                                    self.load_game()
                                else:
                                    self.reset_game()  # brak pliku = nowa gra
                                return
                            else:
                                input_mode = True
                                input_text = ""

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    for rect, i in delete_buttons:
                        if rect and rect.collidepoint(mouse_pos):
                            player_to_remove = players[i]

                            del players[i]
                            with open(players_file, "w") as f:
                                json.dump(players, f)

                            save_file = f"save_{player_to_remove}.json"
                            if os.path.exists(save_file):
                                os.remove(save_file)

                            if player_to_remove == self.current_player:
                                self.current_player = None

                            if not players:
                                input_mode = True
                                input_text = ""
                            break

                    for i, name in enumerate(all_options):
                        y = 130 + i * 40
                        text_rect = pygame.Rect(width // 2 - 150, y - 15, 300, 30)
                        if text_rect.collidepoint(mouse_pos):
                            if i < len(players):
                                self.current_player = players[i]
                                if os.path.exists(f"save_{self.current_player}.json"):
                                    self.load_game()
                                else:
                                    self.reset_game()
                                return
                            else:
                                input_mode = True
                                input_text = ""
