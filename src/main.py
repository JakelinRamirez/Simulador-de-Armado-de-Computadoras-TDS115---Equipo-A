"""
Simulador de Armado de Computadoras - TDS115 Equipo A
Aplicación educativa para aprender sobre componentes de computadoras
"""

import pygame
from screens.selection_screen import SelectionScreen
from screens.start_screen import StartScreen
from screens.simulation_screen import EstanteScreen

def main():
    """Función principal que maneja el flujo de la aplicación"""
    # Inicializar Pygame
    pygame.init()
    
    # Configurar ventana principal
    screen = pygame.display.set_mode((970, 810))
    pygame.display.set_caption("Simulador de Computadoras - TDS115")
    
    # Bucle principal de la aplicación
    while True:
        # Pantalla de inicio
        start_screen = StartScreen(screen)
        if not start_screen.run():
            # Usuario cerró la ventana
            break
            
        # Bucle de selección y simulación
        while True:
            # Pantalla de selección de tipo de computadora
            selection_screen = SelectionScreen(screen)
            selected_type = selection_screen.run()
            
            if not selected_type:
                # Usuario cerró la ventana, salir completamente
                pygame.quit()
                return
            
            print(f"Tipo seleccionado: {selected_type}")
            
            # Pantalla de simulación - pasar el tipo seleccionado
            simulation_screen = EstanteScreen(screen, selected_type)
            go_back = simulation_screen.run()
            
            if not go_back:
                # Usuario cerró la ventana, salir completamente
                pygame.quit()
                return
            
            # Si go_back es True, volver a la pantalla de selección
            # El bucle while True se encarga de esto automáticamente
    
    # Limpiar recursos de Pygame
    pygame.quit()

if __name__ == "__main__":
    main()