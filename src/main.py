"""
Simulador de Armado de Computadoras - TDS115 Equipo A
Aplicación educativa para aprender sobre componentes de computadoras
"""

import pygame
from screens.selection_screen import SelectionScreen
from screens.start_screen import StartScreen
from screens.simulation_screen import EstanteScreen
from screens.worktable_screen import WorktableScreen, WorktableDesktopScreen, LaptopExternalConnectionScreen, DesktopExternalConnectionScreen, LaptopBootScreen

def main():
    """Función principal que maneja el flujo de la aplicación"""
    # Inicializar Pygame
    pygame.init()
    
    # Configurar ventana principal
    screen = pygame.display.set_mode((970, 810))
    pygame.display.set_caption("Simulador de Computadoras - TDS115")
    
    current_screen = "start"  # Restaurar el flujo normal con la pantalla de inicio
    selected_computer_type = None
    final_selected_components = []
    external_components = []  # Para guardar componentes externos separadamente

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
            # Pasar las selecciones previas si existen (cuando se regresa de la mesa de trabajo)
            estante_screen = EstanteScreen(screen, selected_computer_type, final_selected_components if final_selected_components else None)
            estante_result = estante_screen.run_logic()

            if estante_result["action"] == "quit":
                current_screen = "quit"
            elif estante_result["action"] == "back_to_selection":
                current_screen = "selection"
            elif estante_result["action"] == "proceed_to_worktable":
                all_selected_components = estante_result.get("selected_components", [])
                print(f"=== DEBUG: Processing components ===")
                print(f"All selected components: {all_selected_components}")
                
                # Separar componentes internos y externos
                internal_components = []
                selected_external_components = []
                
                # Lista de componentes externos conocidos
                external_component_names = [
                    "Monitor LED 24\"", "Teclado Mecanico", "Mouse Razen", 
                    "Bocinas Estereo", "Webcam HD 1080p", "Microfono USB", 
                    "UPS", "HUB USB"
                ]
                print(f"Known external components: {external_component_names}")
                
                for component in all_selected_components:
                    print(f"Processing component: '{component}'")
                    if component in external_component_names:
                        selected_external_components.append(component)
                        print(f"  -> Classified as EXTERNAL")
                    else:
                        internal_components.append(component)
                        print(f"  -> Classified as INTERNAL")
                
                final_selected_components = internal_components
                external_components = selected_external_components
                print(f"Final internal components: {internal_components}")
                print(f"Final external components: {external_components}")
                print(f"=== End component processing ===")
                current_screen = "worktable"
            else:
                current_screen = "selection"

        elif current_screen == "worktable":
            if selected_computer_type == "laptop":
                worktable = WorktableScreen(screen, selected_computer_type, final_selected_components)
                worktable_action = worktable.run()
            elif selected_computer_type == "desktop":
                worktable = WorktableDesktopScreen(screen, selected_computer_type, final_selected_components)
                worktable_action = worktable.run()
            else:
                # Fallback en caso de tipo no reconocido
                current_screen = "selection"
                continue
                
            # Procesar la acción devuelta por cualquiera de las dos pantallas de mesa de trabajo
            if worktable_action["action"] == "quit":
                current_screen = "quit"
            elif worktable_action["action"] == "back_to_selection":
                # Regresar a la pantalla de componentes con las selecciones preservadas
                final_selected_components = worktable_action.get("selected_components", [])
                current_screen = "estante"
            elif worktable_action["action"] == "assembly_complete":
                print("=== DEBUG: Assembly complete ===")
                print(f"Computer type: {selected_computer_type}")
                print(f"External components list: {external_components}")
                print(f"External components count: {len(external_components)}")
                print(f"Has external components? {bool(external_components)}")
                
                if external_components:
                    # Si hay componentes externos, ir a pantalla de conexión externa (laptop o desktop)
                    print("DEBUG: Going to external_connection screen")
                    current_screen = "external_connection"
                else:
                    # Sin componentes externos, terminar
                    print("DEBUG: Going back to selection (no external components)")
                    current_screen = "selection"
            else:
                current_screen = "selection"

        elif current_screen == "external_connection":
            # Pantalla de conexión de componentes externos (laptop o desktop)
            print("Iniciando pantalla de conexión externa...")
            if selected_computer_type == "laptop":
                external_screen = LaptopExternalConnectionScreen(screen, selected_computer_type, external_components)
            elif selected_computer_type == "desktop":
                external_screen = DesktopExternalConnectionScreen(screen, selected_computer_type, external_components)
            else:
                # Fallback en caso de tipo no reconocido
                current_screen = "selection"
                continue
                
            external_action = external_screen.run()
            
            if external_action["action"] == "quit":
                current_screen = "quit"
            elif external_action["action"] == "back_to_worktable":
                # Regresar a la mesa de trabajo interna
                current_screen = "worktable"
            elif external_action["action"] == "next_to_boot":
                # Para laptop: ir a pantalla de encendido
                if selected_computer_type == "laptop":
                    current_screen = "laptop_boot"
                else:
                    # Para desktop: terminar (no hay pantalla de encendido para desktop)
                    print("¡Ensamble completo!")
                    current_screen = "selection"
            elif external_action["action"] == "assembly_complete":
                # Ensamble completado totalmente
                print("¡Ensamble completo!")
                current_screen = "selection"
            else:
                current_screen = "selection"
        
        elif current_screen == "laptop_boot":
            # Pantalla de encendido de laptop
            print("Iniciando pantalla de encendido de laptop...")
            boot_screen = LaptopBootScreen(screen, final_selected_components)
            boot_action = boot_screen.run()
            
            if boot_action["action"] == "quit":
                current_screen = "quit"
            elif boot_action["action"] == "back_to_selection":
                current_screen = "selection"
            else:
                current_screen = "selection"
    
    # Limpiar recursos de Pygame
    pygame.quit()

if __name__ == "__main__":
    main()