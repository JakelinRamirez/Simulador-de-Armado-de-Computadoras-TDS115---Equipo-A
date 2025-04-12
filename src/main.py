import pygame
from screens.selection_screen import SelectionScreen

pygame.init()
screen = pygame.display.set_mode((800, 600))

selector =SelectionScreen(screen)
tipo = selector.run()
print("Tipo seleccionado:", tipo)

pygame.quit()