import pygame
import sys

pygame.init()

# Stałe
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# Kolory
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
DARK_RED = (150, 0, 0)

# Inicjalizacja okna
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Clicker Game")

clock = pygame.time.Clock()

# Załaduj obrazy
frame_img_orig = pygame.image.load("ramka.png").convert_alpha()
frame_img = pygame.transform.smoothscale(frame_img_orig, (400, 120))

background_img_orig = pygame.image.load("background/background_lvl1.png").convert()
background_img = pygame.transform.scale(background_img_orig, (SCREEN_WIDTH, SCREEN_HEIGHT))

dog_img_orig = pygame.image.load("pies/pies1.png").convert_alpha()
dog_width, dog_height = 300, 300
dog_img = pygame.transform.smoothscale(dog_img_orig, (dog_width, dog_height))

# Czcionki
font_points = pygame.font.SysFont("Arial", 30)
font_button = pygame.font.SysFont("Arial", 20)
font_info = pygame.font.SysFont("Arial", 18)

# Zmienne gry
points = 0
points_per_click = 1
upgrade_cost = 10
info_text = ""
info_color = GREEN
info_timer = 0  # odliczanie do zniknięcia info


def draw_top_panel():
    # Panel górny - ramka + punkty
    panel_x = (screen.get_width() - 400) // 2
    panel_y = 10
    screen.blit(frame_img, (panel_x, panel_y))

    points_text = font_points.render(f"Punkty: {points}", True, BLACK)
    # Wyśrodkowanie tekstu w ramce (400x120)
    text_rect = points_text.get_rect(center=(panel_x + 200, panel_y + 60))
    screen.blit(points_text, text_rect)


def draw_dog():
    x = (screen.get_width() - dog_width) // 2
    y = (screen.get_height() - dog_height) // 2
    screen.blit(dog_img, (x, y))
    return pygame.Rect(x, y, dog_width, dog_height)  # prostokąt do detekcji kliknięć


def draw_bottom_panel():
    # Panel dolny z przyciskiem i info
    button_width = 300
    button_height = 40
    x = (screen.get_width() - button_width) // 2
    y = screen.get_height() - button_height - 20

    # Rysuj przycisk
    mouse_pos = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x, y, button_width, button_height)
    if button_rect.collidepoint(mouse_pos):
        color = DARK_RED
    else:
        color = RED
    pygame.draw.rect(screen, color, button_rect, border_radius=8)

    button_text = font_button.render(f"Ulepsz (+1 za klik) - Koszt: {upgrade_cost}", True, WHITE)
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)

    # Info label pod przyciskiem
    if info_text:
        info_surface = font_info.render(info_text, True, info_color)
        info_rect = info_surface.get_rect(center=(screen.get_width() // 2, y + button_height + 25))
        screen.blit(info_surface, info_rect)

    return button_rect


def show_info(text, color=GREEN, duration=2000):
    global info_text, info_color, info_timer
    info_text = text
    info_color = color
    info_timer = pygame.time.get_ticks() + duration


def main():
    global points, points_per_click, upgrade_cost, info_text, info_timer

    running = True
    while running:
        clock.tick(FPS)

        # Eventy
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                # Przeskaluj tło i ramkę na nowy rozmiar ekranu
                new_w, new_h = event.w, event.h
                pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
                global background_img
                background_img = pygame.transform.scale(background_img_orig, (new_w, new_h))

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                # Klik na psa = dodaj punkty
                dog_rect = draw_dog()  # pobierz aktualny rect psa
                if dog_rect.collidepoint(mouse_pos):
                    points += points_per_click

                # Klik na przycisk ulepszania
                button_rect = draw_bottom_panel()
                if button_rect.collidepoint(mouse_pos):
                    if points >= upgrade_cost:
                        points -= upgrade_cost
                        points_per_click += 1
                        upgrade_cost = int(upgrade_cost * 1.5)
                        show_info("Ulepszenie kupione!", GREEN)
                    else:
                        show_info("Za mało punktów!", (255, 0, 0))

        # Czyszczenie ekranu + rysowanie
        screen.blit(background_img, (0, 0))
        draw_top_panel()
        draw_dog()
        draw_bottom_panel()

        # Ukryj info po czasie
        if info_text and pygame.time.get_ticks() > info_timer:
            info_text = ""

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
