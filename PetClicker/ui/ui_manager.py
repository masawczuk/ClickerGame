import pygame
# Kolory
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
DARK_RED = (150, 0, 0)
PANEL_BG = (240, 240, 240)
DARK_PINK = "#FC0880"
PINK="#FA43A3"

class UIManager:
    def __init__(self, assets):
        self.assets = assets
        self.info_text = ""
        self.info_color = GREEN
        self.info_timer = 0
        self.unlocked_dogs = 1  # Początkowo odblokowany tylko pierwszy piesek
        self.current_dog = 1  # Aktualnie wybrany piesek

        # Panel parameters
        self.panel_width_ratio = 0.3  # oba panele 30% szerokości okna
        self.panel_height = 0

        # Panel 1 (funkcjonalny) - widoczny na start
        self.panel1_visible = False
        self.panel1_target_x = 0
        self.panel1_current_x = 0

        # Panel 2 (pusty) - niewidoczny na start
        self.panel2_visible = True
        self.panel2_target_x = 0
        self.panel2_current_x = 0

        # Przycisk toggle dla paneli
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

        usable_width = int(width * 0.7)
        x = (usable_width - frame.get_width()) // 2
        screen.blit(frame, (x, 10))

        font = pygame.font.SysFont("Arial", int(30 * scale))
        text = font.render(f"Punkty: {points}", True, BLACK)
        rect = text.get_rect(center=(x + frame.get_width() // 2, 45))
        screen.blit(text, rect)

        # Punkty na sekundę
        pps_text = font.render(f"pkt/s: {int(pps)}", True, BLACK)
        pps_rect = pps_text.get_rect(center=(x + frame.get_width() // 2, 75))
        screen.blit(pps_text, pps_rect)

    def draw_right_panel(self, screen, width, height,
                         click_upgrade_costs,
                         ps_upgrade_costs,
                         temp_multiplier_costs):
        panel_width = int(width * self.panel_width_ratio)
        self.panel_height = height

        speed = 20

        # Ustawiamy docelowe pozycje paneli po prawej stronie
        if self.panel1_visible:
            self.panel1_target_x = width - panel_width
        else:
            self.panel1_target_x = width

        if self.panel2_visible:
            self.panel2_target_x = width - panel_width
        else:
            self.panel2_target_x = width

        # Animacja panel 1
        if self.panel1_current_x < self.panel1_target_x:
            self.panel1_current_x = min(self.panel1_current_x + speed, self.panel1_target_x)
        elif self.panel1_current_x > self.panel1_target_x:
            self.panel1_current_x = max(self.panel1_current_x - speed, self.panel1_target_x)

        # Animacja panel 2
        if self.panel2_current_x < self.panel2_target_x:
            self.panel2_current_x = min(self.panel2_current_x + speed, self.panel2_target_x)
        elif self.panel2_current_x > self.panel2_target_x:
            self.panel2_current_x = max(self.panel2_current_x - speed, self.panel2_target_x)

        rects = []

        # Rysowanie panelu 1 (funkcjonalnego)
        if self.panel1_current_x < width:
            pygame.draw.rect(screen, PANEL_BG, (self.panel1_current_x, 0, panel_width, height))

            scale = max(0.5, min(width / 800, 1.2))
            font_btn = pygame.font.SysFont("Arial", int(18 * scale))
            font_info = pygame.font.SysFont("Arial", int(20 * scale))

            btn_width = int(panel_width * 0.8)
            btn_height = int(35 * scale)
            x = self.panel1_current_x + (panel_width - btn_width) // 2

            # Przycisk ulepszenia +1 punkt klik
            y_base = height // 2 - 215

            for i, cost in enumerate(click_upgrade_costs):
                y = y_base + i * 50
                rect = pygame.Rect(x, y, btn_width, btn_height)
                color = DARK_PINK if rect.collidepoint(pygame.mouse.get_pos()) else PINK
                pygame.draw.rect(screen, color, rect, border_radius=8)
                text = font_btn.render(f"Ulepsz klik (+{[1,5,10][i]}) - {cost}", True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
                rects.append(rect)

            # Przycisk ulepszenia punktów na sekundę
            y_base_ps = y_base + 3 * 50 + 20
            for i, cost in enumerate(ps_upgrade_costs):
                y = y_base_ps + i * 50
                rect = pygame.Rect(x, y, btn_width, btn_height)
                color = DARK_PINK if rect.collidepoint(pygame.mouse.get_pos()) else PINK
                pygame.draw.rect(screen, color, rect, border_radius=8)
                text = font_btn.render(f"Punkty/s (+{[1,5,10][i]}) - {cost}", True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
                rects.append(rect)

            # Przycisk ulepszenia mnożnika tymczasowego
            y_base_temp = y_base_ps + 3 * 50 + 20
            durations_sec = [5, 10, 15]
            for i, cost in enumerate(temp_multiplier_costs):
                y = y_base_temp + i * 50
                rect = pygame.Rect(x, y, btn_width, btn_height)
                color = DARK_PINK if rect.collidepoint(pygame.mouse.get_pos()) else PINK
                pygame.draw.rect(screen, color, rect, border_radius=8)
                text = font_btn.render(f"Mnożnik x2 na klik {durations_sec[i]}s - {cost}", True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
                rects.append(rect)

            if self.info_text and pygame.time.get_ticks() < self.info_timer:
                info = font_info.render(self.info_text, True, self.info_color)
                info_rect = info.get_rect(center=(self.panel1_current_x + panel_width // 2, y_base_temp + 3 * 43 + 30))
                screen.blit(info, info_rect)

        # Rysowanie panelu 2 (z opisem gry)
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

        if self.panel2_current_x < width:
            pygame.draw.rect(screen, PANEL_BG, (self.panel2_current_x, 0, panel_width, height))

            scale = max(0.4, min(width / 900, 0.9))
            margin_x = self.panel2_current_x + 20
            current_y = 30

            font_title = pygame.font.SysFont("Verdana", int(20 * scale), bold=True)
            font_subtitle = pygame.font.SysFont("Verdana", int(16 * scale), bold=True)
            font_text = pygame.font.SysFont("Verdana", int(15 * scale))



            max_text_width = panel_width - 30  # zostawiamy margines po obu stronach
            indent = 20

            description_sections = [
                ("Witaj w PET CLICKER!", font_title, 0),  # tytuł główny bez wcięcia
                ("Klikaj na swojego pupila, aby zdobywać punkty. Wymieniaj je na ulepszenia w panelu po prawej stronie.", font_text, 0),

                ("Ulepszenia i niespodzianki", font_subtitle, 0),  # nagłówek bez wcięcia
                ("Za zakupione ulepszenia możesz otrzymać nagrodę:", font_text, 0),
                ("- nowe tło lub", font_text, 20),  # podpunkty z wcięciem
                ("- nowego pieska!", font_text, 20),

                ("Zapis i zarządzanie grą", font_subtitle, 0),  # nagłówek bez wcięcia
                ("Przyciski po lewej stronie:", font_text,0),  # podpunkty z wcięciem
                ("- Dyskietka - Zapisz stan gry.", font_text, 20),  # podpunkty z wcięciem
                ("- Pad - Restartuj grę i zacznij od nowa.", font_text, 20),
                ("- Ikona gracza - Wybierz gracza (użyj strzałek na klawiaturze).", font_text, 20),
                ("Uwaga! Niezapisane zmiany zostaną utracone po opuszczeniu gry.", font_subtitle, 0)
            ]

            section_spacing = int(7 * scale)  # większy odstęp między sekcjami
            line_spacing = int(24 * scale)

            for text, font, left_indent in description_sections:
                # Dzielimy tekst na linie, które mieszczą się w panelu (z uwzględnieniem wcięcia)
                wrapped_lines = wrap_text(text, font, max_text_width - left_indent)

                for line in wrapped_lines:
                    rendered_line = font.render(line, True, BLACK)
                    screen.blit(rendered_line, (margin_x + left_indent, current_y))
                    current_y += line_spacing

                current_y += section_spacing  # odstęp po każdej sekcji

        # Rysujemy przyciski toggle dla obu paneli
        arrow_y = 1

        # Toggle button dla panel 1
        arrow_x1 = self.panel1_current_x - self.toggle_button_width if self.panel1_visible else width - self.toggle_button_width
        self.toggle_button_rect1 = pygame.Rect(arrow_x1, arrow_y, self.toggle_button_width, self.toggle_button_height)
        pygame.draw.rect(screen, DARK_PINK, self.toggle_button_rect1)
        arrow1 = "<" if self.panel1_visible else ">"
        font_arrow = pygame.font.SysFont("Arial", 30)
        arrow_text1 = font_arrow.render(arrow1, True, WHITE)
        arrow_rect1 = arrow_text1.get_rect(center=self.toggle_button_rect1.center)
        screen.blit(arrow_text1, arrow_rect1)

        # Toggle button dla panel 2
        arrow_x2 = self.panel2_current_x - self.toggle_button_width if self.panel2_visible else width - self.toggle_button_width
        self.toggle_button_rect2 = pygame.Rect(arrow_x2, arrow_y + self.toggle_button_height + 1,
                                               self.toggle_button_width, self.toggle_button_height)
        pygame.draw.rect(screen, PINK, self.toggle_button_rect2)
        arrow2 = "<" if self.panel2_visible else ">"
        arrow_text2 = font_arrow.render(arrow2, True, WHITE)
        arrow_rect2 = arrow_text2.get_rect(center=self.toggle_button_rect2.center)
        screen.blit(arrow_text2, arrow_rect2)

        return rects

    def toggle_panel(self, panel_name, screen_width):
        # Jeśli kliknięto toggle na panel 1
        if panel_name == "panel1":
            if self.panel1_visible:
                self.panel1_visible = False
            else:
                self.panel1_visible = True
                self.panel2_visible = False  # drugi panel schowany, bo nie chcemy dwóch naraz

        # Jeśli kliknięto toggle na panel 2
        elif panel_name == "panel2":
            if self.panel2_visible:
                self.panel2_visible = False
            else:
                self.panel2_visible = True
                self.panel1_visible = False  # pierwszy panel schowany

        # Reset pozycji docelowych na podstawie nowych widoczności
        panel_width = int(screen_width * self.panel_width_ratio)
        if self.panel1_visible:
            self.panel1_target_x = screen_width - panel_width
        else:
            self.panel1_target_x = screen_width

        if self.panel2_visible:
            self.panel2_target_x = screen_width - panel_width
        else:
            self.panel2_target_x = screen_width