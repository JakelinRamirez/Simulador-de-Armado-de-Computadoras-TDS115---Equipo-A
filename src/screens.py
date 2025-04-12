import pygame
def show_start_screen(screen, screen_width, screen_height):
    # Tu código aquí que usa el objeto `screen`
    # Ejemplo de código para mostrar un mensaje en la pantalla
    font = pygame.font.Font(None, 36)
    text = font.render("Bienvenido al Simulador", True, (255, 255, 255))
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
    pygame.display.update()