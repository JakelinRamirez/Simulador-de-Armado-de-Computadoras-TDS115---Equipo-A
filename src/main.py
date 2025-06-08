import pygame
import unicodedata
from screens.selection_screen import SelectionScreen
from screens.start_screen import StartScreen
from screens.simulation_screen import EstanteScreen
from screens.worktable_screen import WorktableScreen, WorktableDesktopScreen

def normalizar(texto):
    """Normaliza texto para evitar diferencias de formato al comparar"""
    texto = texto.lower().strip()
    texto = texto.replace("″", "\"")  # Comillas curvas a rectas
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    return texto

def equipo_encendido(tipo, componentes_seleccionados):
    """Verifica si el equipo tiene todos los componentes esenciales para encender"""
    COMPONENTES_REQUERIDOS = {
        "desktop": [
            "RAM DDR4 8GB",
            "Ryzen 7 5700X",
            "Kingston SSD 1TB",
            "Cooler Master H212",
            "Ventilador ARGB",
            "PSU 600W"
        ],
        "laptop": [
            "Ryzen 7 5700X",
            "RAM DDR4 8GB",
            "Kingston SSD 1TB"
        ]
    }
    requeridos = [normalizar(comp) for comp in COMPONENTES_REQUERIDOS.get(tipo, [])]

    # IMPORTANTE: Aquí imprime los requeridos para ver qué se está comparando
    print("Componentes requeridos normalizados:", requeridos)

    seleccionados = [normalizar(comp) for comp in componentes_seleccionados]

    # IMPORTANTE: Aquí imprime los seleccionados para ver qué está realmente seleccionando el usuario
    print("Componentes seleccionados normalizados:", seleccionados)

    return all(req in seleccionados for req in requeridos)


def mostrar_mensaje(screen, mensaje):
    """Muestra un mensaje centrado en la pantalla"""
    font = pygame.font.SysFont(None, 50)
    text = font.render(mensaje, True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width()//2, 70))
    screen.blit(text, text_rect)

def main():
    """Función principal que maneja el flujo de la aplicación"""
    pygame.init()
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
            estante_screen = EstanteScreen(
                screen,
                selected_computer_type,
                final_selected_components if final_selected_components else None
            )
            estante_result = estante_screen.run_logic()

            if estante_result["action"] == "quit":
                current_screen = "quit"
            elif estante_result["action"] == "back_to_selection":
                current_screen = "selection"
            elif estante_result["action"] == "proceed_to_worktable":
                final_selected_components = estante_result.get("selected_components", [])
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
                current_screen = "selection"
                continue

            if worktable_action["action"] == "quit":
                current_screen = "quit"
            elif worktable_action["action"] == "back_to_selection":
                final_selected_components = worktable_action.get("selected_components", [])
                current_screen = "estante"
            elif worktable_action["action"] == "assembly_complete":
                final_selected_components = worktable_action.get("selected_components", [])
                print("Lista final antes de verificar encendido:", final_selected_components)
                # Mostrar si el equipo enciende o no
                encendido = equipo_encendido(selected_computer_type, final_selected_components)

                # DEBUG: imprimir componentes seleccionados y normalizados
                print("Componentes seleccionados:", final_selected_components)
                print("Normalizados:", [normalizar(c) for c in final_selected_components])

                if selected_computer_type == "desktop":
                    img_path = "assets/images/pc_on.png" if encendido else "assets/images/pc_off.png"
                    mensaje = "PC Ensamblada" if encendido else "Volver a Ensamblar"
                else:
                    img_path = "assets/images/laptop_on.png" if encendido else "assets/images/laptop_off.png"
                    mensaje = "Laptop Ensamblada" if encendido else "Volver a Ensamblar"

                imagen = pygame.image.load(img_path)
                screen.fill((0, 0, 0))  # Fondo negro
                screen.blit(imagen, (150, 100))  # Ajusta posición si es necesario
                mostrar_mensaje(screen, mensaje)
                pygame.display.flip()
                pygame.time.delay(3000)  # Mostrar imagen por 3 segundos

                current_screen = "selection"
            else:
                current_screen = "selection"
        else:
            current_screen = "selection"

    pygame.quit()

if __name__ == "__main__":
    main()
