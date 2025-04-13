import pygame
from screens.selection_screen import SelectionScreen
from screens.start_screen import StartScreen
from screens.simulation_screen import EstanteScreen  

pygame.init()
screen = pygame.display.set_mode((800, 600))

# Mostrar pantalla de start o de inicio
login = StartScreen(screen)
if login.run():  # Si el usuario hace clic en "Iniciar Simulación"
    selector = SelectionScreen(screen)
    tipo = selector.run()
    print("Tipo seleccionado:", tipo)
# Si eligió laptop o desktop, inicia simulación
if tipo:
    simulation = EstanteScreen(screen)
    simulation.run()

pygame.quit()