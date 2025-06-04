import pygame

# Kolory
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
PANEL_BG = (240, 240, 240)
DARK_PINK = "#FC0880"
PINK = "#FA43A3"

# Stałe
CLICK_VALUES = [1, 5, 10]
TEMP_DURATIONS = [5, 10, 15]
BUTTON_SPACING = 50
BUTTON_HEIGHT_RATIO = 35
BUTTON_WIDTH_RATIO = 0.8
PANEL_WIDTH_RATIO = 0.3
PANEL_ANIMATION_SPEED = 20


class UIManager:
    def __init__(self, assets):
        self.assets = assets
        self.info_text = ""
        self.info_color = GREEN
        self.info_timer = 0
        self.unlocked_dogs = 1
        self.current_dog = 1

        self.panel1_visible = False
        self.panel2_visible = True

        self.panel1_current_x = self.panel2_current_x = 0
        self.panel1_target_x = self.panel2_target_x = 0

        self.toggle_button_width = 40
        self.toggle_button_height = 40
        self.toggle_button_rect1 = pygame.Rect(0, 0, self.toggle_button_width, self.toggle_button_height)
        self.toggle_button_rect2 = pygame.Rect(0, 0, self.toggle_button_width, self.toggle_button_height)

    def show_info(self, text, color=GREEN, duration=2000):
        self.info_text = text
        self.info_color = color
        self.info_timer = pygame.time.get_ticks() + duration

    def draw_top_panel(self, screen, width, points, pps):
        scale = max(0.5, min(width / 800, 0.85))
        frame = pygame.transform.smoothscale(self.assets.frame, (int(400 * scale), int(120 * scale)))

        usable_width = int(width * (1 - PANEL_WIDTH_RATIO))
        x = (usable_width - frame.get_width()) // 2
        screen.blit(frame, (x, 10))

        font = pygame.font.SysFont("Arial", int(30 * scale))
        text = font.render(f"Punkty: {points}", True, BLACK)
        screen.blit(text, text.get_rect(center=(x + frame.get_width() // 2, 45)))

        pps_text = font.render(f"pkt/s: {int(pps)}", True, BLACK)
        screen.blit(pps_text, pps_text.get_rect(center=(x + frame.get_width() // 2, 75)))

    def draw_button(self, screen, rect, text, font, hover_color, base_color):
        color = hover_color if rect.collidepoint(pygame.mouse.get_pos()) else base_color
        pygame.draw.rect(screen, color, rect, border_radius=8)
        text_surface = font.render(text, True, WHITE)
        screen.blit(text_surface, text_surface.get_rect(center=rect.center))

    def animate_panel(self, current_x, target_x):
        if current_x < target_x:
            return min(current_x + PANEL_ANIMATION_SPEED, target_x)
        elif current_x > target_x:
            return max(current_x - PANEL_ANIMATION_SPEED, target_x)
        return current_x

    def draw_right_panel(self, screen, width, height,
                         click_upgrade_costs,
                         ps_upgrade_costs,
                         temp_multiplier_costs):

        panel_width = int(width * PANEL_WIDTH_RATIO)
        self.panel_height = height

        # Aktualizacja pozycji
        self.panel1_target_x = width - panel_width if self.panel1_visible else width
        self.panel2_target_x = width - panel_width if self.panel2_visible else width

        self.panel1_current_x = self.animate_panel(self.panel1_current_x, self.panel1_target_x)
        self.panel2_current_x = self.animate_panel(self.panel2_current_x, self.panel2_target_x)

        rects = []

        # Rysowanie panelu 1
        if self.panel1_current_x < width:
            pygame.draw.rect(screen, PANEL_BG, (self.panel1_current_x, 0, panel_width, height))

            scale = max(0.5, min(width / 800, 1.2))
            font_btn = pygame.font.SysFont("Arial", int(18 * scale))
            font_info = pygame.font.SysFont("Arial", int(20 * scale))

            btn_width = int(panel_width * BUTTON_WIDTH_RATIO)
            btn_height = int(BUTTON_HEIGHT_RATIO * scale)
            x = self.panel1_current_x + (panel_width - btn_width) // 2
            y = height // 2 - 215

            for i, cost in enumerate(click_upgrade_costs):
                rect = pygame.Rect(x, y + i * BUTTON_SPACING, btn_width, btn_height)
                self.draw_button(screen, rect, f"Ulepsz klik (+{CLICK_VALUES[i]}) - {cost}", font_btn, DARK_PINK, PINK)
                rects.append(rect)

            y += 3 * BUTTON_SPACING + 20
            for i, cost in enumerate(ps_upgrade_costs):
                rect = pygame.Rect(x, y + i * BUTTON_SPACING, btn_width, btn_height)
                self.draw_button(screen, rect, f"Punkty/s (+{CLICK_VALUES[i]}) - {cost}", font_btn, DARK_PINK, PINK)
                rects.append(rect)

            y += 3 * BUTTON_SPACING + 20
            for i, cost in enumerate(temp_multiplier_costs):
                rect = pygame.Rect(x, y + i * BUTTON_SPACING, btn_width, btn_height)
                self.draw_button(screen, rect, f"Mnożnik x2 na klik {TEMP_DURATIONS[i]}s - {cost}", font_btn, DARK_PINK,
                                 PINK)
                rects.append(rect)

            if self.info_text and pygame.time.get_ticks() < self.info_timer:
                info = font_info.render(self.info_text, True, self.info_color)
                screen.blit(info, info.get_rect(center=(self.panel1_current_x + panel_width // 2, y + 3 * 43 + 30)))

        # Rysowanie panelu 2 (z opisem gry)
        if self.panel2_current_x < width:
            pygame.draw.rect(screen, PANEL_BG, (self.panel2_current_x, 0, panel_width, height))

            scale = max(0.4, min(width / 900, 0.9))
            margin_x = self.panel2_current_x + 20
            current_y = 30

            font_title = pygame.font.SysFont("Verdana", int(20 * scale), bold=True)
            font_subtitle = pygame.font.SysFont("Verdana", int(16 * scale), bold=True)
            font_text = pygame.font.SysFont("Verdana", int(15 * scale))

            max_text_width = panel_width - 30
            indent = 20

            description_sections = [
                ("Witaj w PET CLICKER!", font_title, 0),
                (
"Klikaj na swojego pupila, aby zdobywać punkty. Wymieniaj je na ulepszenia w panelu po prawej stronie.",
                font_text, 0),

                ("Ulepszenia i niespodzianki", font_subtitle, 0),
                ("Za zakupione ulepszenia możesz otrzymać nagrodę:", font_text, 0),
                ("- nowe tło lub", font_text, indent),
                ("- nowego pieska!", font_text, indent),

                ("Zapis i zarządzanie grą", font_subtitle, 0),
                ("Przyciski po lewej stronie:", font_text, 0),
                ("- Dyskietka - Zapisz stan gry.", font_text, indent),
                ("- Pad - Restartuj grę i zacznij od nowa.", font_text, indent),
                ("- Ikona gracza - Wybierz gracza (użyj strzałek na klawiaturze).", font_text, indent),
                ("Uwaga! Niezapisane zmiany zostaną utracone po opuszczeniu gry.", font_subtitle, 0)
            ]

            section_spacing = int(7 * scale)
            line_spacing = int(24 * scale)

            for text, font, left_indent in description_sections:
                wrapped = self.wrap_text(text, font, max_text_width - left_indent)
                for line in wrapped:
                    rendered = font.render(line, True, BLACK)
                    screen.blit(rendered, (margin_x + left_indent, current_y))
                    current_y += line_spacing
                current_y += section_spacing

        # Toggle buttons
        arrow_y = 1

        # Toggle button panel 1
        arrow_x1 = self.panel1_current_x - self.toggle_button_width if self.panel1_visible else width - self.toggle_button_width
        self.toggle_button_rect1 = pygame.Rect(arrow_x1, arrow_y, self.toggle_button_width, self.toggle_button_height)
        pygame.draw.rect(screen, DARK_PINK, self.toggle_button_rect1)
        self._draw_arrow(screen, self.toggle_button_rect1, "<" if self.panel1_visible else ">")

        # Toggle button panel 2
        arrow_x2 = self.panel2_current_x - self.toggle_button_width if self.panel2_visible else width - self.toggle_button_width
        self.toggle_button_rect2 = pygame.Rect(arrow_x2, arrow_y + self.toggle_button_height + 1,
                                               self.toggle_button_width, self.toggle_button_height)
        pygame.draw.rect(screen, PINK, self.toggle_button_rect2)
        self._draw_arrow(screen, self.toggle_button_rect2, "<" if self.panel2_visible else ">")

        return rects

    def _draw_arrow(self, screen, rect, symbol):
        font_arrow = pygame.font.SysFont("Arial", 30)
        text = font_arrow.render(symbol, True, WHITE)
        screen.blit(text, text.get_rect(center=rect.center))

    def toggle_panel(self, panel_name, screen_width):
        if panel_name == "panel1":
            self.panel1_visible = not self.panel1_visible
            self.panel2_visible = False if self.panel1_visible else self.panel2_visible
        elif panel_name == "panel2":
            self.panel2_visible = not self.panel2_visible
            self.panel1_visible = False if self.panel2_visible else self.panel1_visible

    @staticmethod
    def wrap_text(text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        return lines