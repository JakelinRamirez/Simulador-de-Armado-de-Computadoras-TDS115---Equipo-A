"""
Simulador de Armado de Computadoras - TDS115 Equipo A
Aplicación educativa para aprender sobre componentes de computadoras
"""

import pygame
from screens.selection_screen import SelectionScreen
from screens.start_screen import StartScreen
from screens.simulation_screen import EstanteScreen
from screens.worktable_screen import WorktableScreen

def main():
    """Función principal que maneja el flujo de la aplicación"""
    # Inicializar Pygame
    pygame.init()
    
    # Configurar ventana principal
    screen = pygame.display.set_mode((970, 810))
    pygame.display.set_caption("Simulador de Computadoras - TDS115")
    
    current_screen = "start"
    selected_computer_type = None
    final_selected_components = []

    while current_screen != "quit":
        if current_screen == "start":
            start_screen = StartScreen(screen)
            if not start_screen.run():
                current_screen = "quit"
            else:
                current_screen = "selection"
        
        elif current_screen == "selection":
            selection_screen = SelectionScreen(screen)
            selected_computer_type = selection_screen.run()
            if not selected_computer_type:
                current_screen = "quit"
            else:
                print(f"Tipo seleccionado: {selected_computer_type}")
                current_screen = "estante"
                final_selected_components = []
        
        elif current_screen == "estante":
            estante_screen = EstanteScreen(screen, selected_computer_type)
            estante_result = estante_screen.run_logic()

            if estante_result["action"] == "quit":
                current_screen = "quit"
            elif estante_result["action"] == "back_to_selection":
                current_screen = "selection"
            elif estante_result["action"] == "proceed_to_worktable" and selected_computer_type == "laptop":
                final_selected_components = estante_result.get("selected_components", [])
                current_screen = "worktable"
            else:
                current_screen = "selection"

        elif current_screen == "worktable":
            if selected_computer_type == "laptop":
                worktable = WorktableScreen(screen, selected_computer_type, final_selected_components)
                worktable_action = worktable.run()
                if worktable_action["action"] == "quit":
                    current_screen = "quit"
                else:
                    current_screen = "selection"
            else:
                current_screen = "selection"
    
    # Limpiar recursos de Pygame
    pygame.quit()

if __name__ == "__main__":
    main()