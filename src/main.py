import pygame
import sys
from screens import show_start_screen

# Inicializar Pygame
pygame.init()

# Configuración de la ventana
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simulador de Armado de Computadoras")

# Bucle principal del juego
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Llamar a la pantalla de inicio
    show_start_screen(screen, screen_width, screen_height)

pygame.quit()