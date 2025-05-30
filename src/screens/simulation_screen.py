import pygame

class EstanteScreen:
    """Pantalla de simulación con estantes de componentes internos y externos"""
    
    def __init__(self, screen):
        # Configuración básica de pantalla
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Paleta de colores coherente
        self.bg_color = (15, 23, 42)         # Azul marino oscuro
        self.component_internal = (34, 197, 94)   # Verde para internos
        self.component_external = (239, 68, 68)   # Rojo para externos
        self.component_hover = (255, 255, 255)    # Blanco para hover
        self.text_color = (248, 250, 252)     # Blanco hueso
        self.button_color = (37, 99, 235)     # Azul botón
        self.button_hover = (29, 78, 216)     # Azul hover
        self.back_button_color = (107, 114, 128)  # Gris para botón atrás
        self.back_button_hover = (75, 85, 99)     # Gris hover
        
        # Fuentes
        self.title_font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 24)
        self.component_font = pygame.font.Font(None, 20)
        
        # Títulos de los estantes
        self.internal_text = self.title_font.render("Componentes Internos", True, self.text_color)
        self.external_text = self.title_font.render("Componentes Externos", True, self.text_color)
        
        # Nombres de componentes internos
        self.internal_names = [
            "CPU", "RAM", "GPU", "Motherboard", "PSU",
            "HDD", "SSD", "Cooler", "Case Fan", "BIOS",
            "Wifi Card", "Sound Card"
        ]
        
        # Nombres de componentes externos
        self.external_names = [
            "Monitor", "Keyboard", "Mouse", "Speakers",
            "Webcam", "Printer", "Headphones", "Microphone"
        ]
        
        # Crear componentes internos (3 filas de 4)
        self.internal_components = []
        self.internal_labels = []
        for i in range(12):
            row = i // 4
            col = i % 4
            x = 120 + col * 140
            y = 120 + row * 80
            self.internal_components.append(pygame.Rect(x, y, 120, 60))
        
        # Crear componentes externos (2 filas de 4)
        self.external_components = []
        self.external_labels = []
        for i in range(8):
            row = i // 4
            col = i % 4
            x = 120 + col * 140
            y = 180 + row * 100
            self.external_components.append(pygame.Rect(x, y, 120, 70))
        
        # Botón para cambiar estante
        self.switch_button_rect = pygame.Rect(320, 480, 160, 50)
        
        # Botón para regresar (nuevo)
        self.back_button_rect = pygame.Rect(50, 50, 120, 45)
        
        # Estados
        self.show_internal = True
        self.switch_hovered = False
        self.back_hovered = False
        self.component_hovered = -1  # Índice del componente con hover
    
    def draw_gradient_rect(self, rect, color1, color2):
        """Dibuja un rectángulo con gradiente vertical"""
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), 
                           (rect.x, rect.y + y), 
                           (rect.x + rect.width, rect.y + y))
    
    def draw_component(self, rect, name, base_color, is_hovered):
        """Dibuja un componente individual con su etiqueta"""
        # Color según estado
        color = self.component_hover if is_hovered else base_color
        
        # Sombra del componente
        shadow_rect = rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(self.screen, (0, 0, 0, 40), shadow_rect, border_radius=10)
        
        # Componente principal
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        
        # Borde
        border_color = (255, 255, 255) if is_hovered else (100, 116, 139)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=10)
        
        # Texto del componente
        text_color = (0, 0, 0) if is_hovered else (255, 255, 255)
        text = self.component_font.render(name, True, text_color)
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)
    
    def draw_button(self, rect, text, base_color, hover_color, is_hovered):
        """Dibuja un botón con efecto hover"""
        # Sombra
        shadow_rect = rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(self.screen, (0, 0, 0, 50), shadow_rect, border_radius=12)
        
        # Botón
        color = hover_color if is_hovered else base_color
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        
        # Texto
        button_text = self.button_font.render(text, True, self.text_color)
        text_rect = button_text.get_rect(center=rect.center)
        self.screen.blit(button_text, text_rect)

    def draw(self):
        """Renderiza todos los elementos de la pantalla"""
        # Fondo con gradiente
        self.draw_gradient_rect(pygame.Rect(0, 0, self.width, self.height), 
                               self.bg_color, (25, 33, 52))
        
        # Botón de retroceso
        self.draw_button(self.back_button_rect, "< Atras", 
                        self.back_button_color, self.back_button_hover, self.back_hovered)
        
        # Título del estante actual
        if self.show_internal:
            title_rect = self.internal_text.get_rect(center=(self.width // 2, 80))
            self.screen.blit(self.internal_text, title_rect)
            
            # Dibujar componentes internos
            for i, (rect, name) in enumerate(zip(self.internal_components, self.internal_names)):
                is_hovered = (self.component_hovered == i)
                self.draw_component(rect, name, self.component_internal, is_hovered)
                
        else:
            title_rect = self.external_text.get_rect(center=(self.width // 2, 80))
            self.screen.blit(self.external_text, title_rect)
            
            # Dibujar componentes externos
            for i, (rect, name) in enumerate(zip(self.external_components, self.external_names)):
                is_hovered = (self.component_hovered == i)
                self.draw_component(rect, name, self.component_external, is_hovered)
        
        # Botón cambiar estante
        switch_text = "Ver Externos" if self.show_internal else "Ver Internos"
        self.draw_button(self.switch_button_rect, switch_text,
                        self.button_color, self.button_hover, self.switch_hovered)
        
        # Instrucciones en la parte inferior
        instruction_text = "Haz clic en los componentes para aprender más"
        instruction = self.component_font.render(instruction_text, True, (156, 163, 175))
        instruction_rect = instruction.get_rect(center=(self.width // 2, 550))
        self.screen.blit(instruction, instruction_rect)
        
        pygame.display.flip()

    def run(self):
        """Maneja eventos y lógica principal de la simulación"""
        running = True
        go_back = False
        
        while running:
            # Detectar hover en botones y componentes
            mouse_pos = pygame.mouse.get_pos()
            self.switch_hovered = self.switch_button_rect.collidepoint(mouse_pos)
            self.back_hovered = self.back_button_rect.collidepoint(mouse_pos)
            
            # Detectar hover en componentes
            self.component_hovered = -1
            if self.show_internal:
                for i, rect in enumerate(self.internal_components):
                    if rect.collidepoint(mouse_pos):
                        self.component_hovered = i
                        break
            else:
                for i, rect in enumerate(self.external_components):
                    if rect.collidepoint(mouse_pos):
                        self.component_hovered = i
                        break
            
            self.draw()
            
            # Procesar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.switch_button_rect.collidepoint(event.pos):
                        # Cambiar entre estantes
                        self.show_internal = not self.show_internal
                    elif self.back_button_rect.collidepoint(event.pos):
                        # Regresar a selección
                        go_back = True
                        running = False
                    else:
                        # Clic en componente (aquí se puede agregar lógica futura)
                        if self.show_internal:
                            for i, rect in enumerate(self.internal_components):
                                if rect.collidepoint(event.pos):
                                    print(f"Componente seleccionado: {self.internal_names[i]}")
                        else:
                            for i, rect in enumerate(self.external_components):
                                if rect.collidepoint(event.pos):
                                    print(f"Componente seleccionado: {self.external_names[i]}")
        
        return go_back