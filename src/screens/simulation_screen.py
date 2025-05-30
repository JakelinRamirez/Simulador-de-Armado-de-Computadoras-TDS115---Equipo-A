import pygame

class ComponentCard:
    """Representa una tarjeta individual de componente"""
    
    def __init__(self, name, image_path, category, rect):
        self.name = name
        self.image_path = image_path
        self.category = category
        self.rect = rect
        self.selected = False
        # Botón ajustado para nuevas dimensiones de tarjeta
        self.button_rect = pygame.Rect(rect.x + 20, rect.y + rect.height - 38, rect.width - 40, 30) # Botón un poco más alto
        
        # Cargar imagen del componente
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            # Imagen cuadrada y un poco más grande
            img_size = (100, 100)
            self.image = pygame.transform.scale(self.image, img_size)
        except:
            # Crear imagen placeholder si no se puede cargar
            self.image = pygame.Surface((100, 100))
            self.image.fill((100, 100, 100))

class ConfirmDialog:
    """Diálogo de confirmación o aviso"""
    
    def __init__(self, screen, message, is_alert=False):
        self.screen = screen
        self.message = message
        self.is_alert = is_alert 
        self.width = 400
        self.height = 160 if is_alert else 200 # Ligeramente más alto para alertas con texto de 3 líneas
        self.rect = pygame.Rect(
            (screen.get_width() - self.width) // 2,
            (screen.get_height() - self.height) // 2,
            self.width, self.height
        )
        
        button_width, button_height = 120, 40
        if self.is_alert:
            # Botón OK para alertas, centrado y más abajo
            self.ok_button = pygame.Rect(
                self.rect.centerx - button_width // 2, 
                self.rect.y + self.height - 55, # Más abajo (antes -60)
                button_width, button_height
            )
        else:
            # Botones Sí/No para confirmaciones
            self.yes_button = pygame.Rect(
                self.rect.x + 50, self.rect.y + self.height - 70, button_width, button_height
            )
            self.no_button = pygame.Rect(
                self.rect.x + 230, self.rect.y + self.height - 70, button_width, button_height
            )
        
        # Colores
        self.bg_color = (30, 41, 59)
        self.text_color = (248, 250, 252)
        self.yes_color = (239, 68, 68)    # Rojo para descartar
        self.no_color = (34, 197, 94)     # Verde para continuar/OK
        self.ok_color = (59, 130, 246)    # Azul para OK en alertas
        
        # Fuentes
        self.font = pygame.font.Font(None, 24)
        self.button_font = pygame.font.Font(None, 20)
    
    def draw(self):
        """Dibuja el diálogo"""
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        pygame.draw.rect(self.screen, self.bg_color, self.rect, border_radius=15)
        pygame.draw.rect(self.screen, (71, 85, 105), self.rect, 3, border_radius=15)
        
        lines = self.message.split('\n')
        # Ajustar el v_offset para el texto en modo alerta para dar más espacio al botón OK
        text_start_y = self.rect.y + 25 # Empezar texto más arriba
        line_height = 22 # Espacio entre líneas de texto

        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, self.text_color)
            text_rect = text_surface.get_rect(center=(self.rect.centerx, text_start_y + i * line_height))
            self.screen.blit(text_surface, text_rect)
        
        if self.is_alert:
            pygame.draw.rect(self.screen, self.ok_color, self.ok_button, border_radius=8)
            ok_text = self.button_font.render("OK", True, self.text_color)
            ok_text_rect = ok_text.get_rect(center=self.ok_button.center)
            self.screen.blit(ok_text, ok_text_rect)
        else:
            pygame.draw.rect(self.screen, self.yes_color, self.yes_button, border_radius=8)
            yes_text = self.button_font.render("Descartar", True, self.text_color)
            yes_text_rect = yes_text.get_rect(center=self.yes_button.center)
            self.screen.blit(yes_text, yes_text_rect)
            
            pygame.draw.rect(self.screen, self.no_color, self.no_button, border_radius=8)
            no_text = self.button_font.render("Continuar", True, self.text_color)
            no_text_rect = no_text.get_rect(center=self.no_button.center)
            self.screen.blit(no_text, no_text_rect)
    
    def handle_click(self, pos):
        """Maneja clics. Para alertas, solo cierra el diálogo (retorna True). Para confirmación, sigue igual."""
        if self.is_alert:
            if self.ok_button.collidepoint(pos):
                return True # Indica que la alerta fue cerrada
            return False # Clic fuera del botón OK, no cierra
        else:
            if self.yes_button.collidepoint(pos):
                return True  # Descartar cambios / Sí
            elif self.no_button.collidepoint(pos):
                return False # Continuar con los cambios / No
            return None # Clic fuera de los botones de confirmación

class EstanteScreen:
    """Pantalla de simulación con estantes de componentes modernos"""
    
    def __init__(self, screen, computer_type):
        # Configuración básica
        self.screen = screen
        self.computer_type = computer_type # Guardar el tipo de computadora
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Paleta de colores moderna
        self.bg_color = (248, 250, 252)     # Fondo blanco
        self.card_color = (255, 255, 255)   # Blanco para tarjetas
        self.selected_color = (34, 197, 94) # Verde para seleccionados
        self.disabled_color = (203, 213, 225) # Gris claro para deshabilitados
        self.disabled_text_color = (100, 116, 139) # Texto gris para deshabilitados
        self.button_color = (59, 130, 246)  # Azul para botones
        self.button_hover = (37, 99, 235)   # Azul hover
        self.text_color = (15, 23, 42)      # Texto oscuro
        self.category_bg = (59, 130, 246)   # Fondo de categorías
        self.category_text = (255, 255, 255) # Texto de categorías
        self.type_indicator_bg = (22, 163, 74) # Verde oscuro para el fondo del indicador
        self.type_indicator_text = (240, 253, 244) # Texto casi blanco para el indicador
        
        # Fuentes
        self.title_font = pygame.font.Font(None, 32)
        self.category_font = pygame.font.Font(None, 24)
        self.component_font = pygame.font.Font(None, 18)
        self.button_font = pygame.font.Font(None, 16)
        self.type_indicator_font = pygame.font.Font(None, 18) # Fuente para el indicador
        
        # Estado actual
        self.show_internal = True
        self.selected_components = []
        self.dialog = None
        
        # Crear componentes
        self.setup_components()
        
        # Botones de navegación
        self.setup_navigation_buttons()

        # Preparar texto del indicador de tipo de PC
        type_text = f"Selección: {self.computer_type.capitalize()}"
        self.type_indicator_surface = self.type_indicator_font.render(type_text, True, self.type_indicator_text)
        padding = 10
        self.type_indicator_rect = pygame.Rect(
            self.width - self.type_indicator_surface.get_width() - padding * 2 - 15, # 15px margen derecho
            15, # 15px margen superior
            self.type_indicator_surface.get_width() + padding * 2,
            self.type_indicator_surface.get_height() + padding
        )
    
    def setup_components(self):
        """Configura todos los componentes con sus categorías para ventana de 970x810"""
        self.internal_components = []
        common_internal = [
            ("RAM DDR4 8GB", "assets/images/componentesInternos/ram.png"),
            ("Ryzen 7 5700X", "assets/images/componentesInternos/cpu.png"),
            ("Kingston SSD 1TB", "assets/images/componentesInternos/ssd.png"),
            ("M.2 NVMe SSD", "assets/images/componentesInternos/m.2.png"),
            ("Modulo Wi-Fi/BT", "assets/images/componentesInternos/módulo Wi-Fi:Bluetooth.png"),
        ]
        desktop_only = [
            ("NVIDIA RTX 3060", "assets/images/componentesInternos/gpu.png"),
            ("ASUS Prime B550M", "assets/images/componentesInternos/motherboard.png"),
            ("Cooler Master H212", "assets/images/componentesInternos/Cooler Master Hyper 212.png"),
            ("Ventilador ARGB", "assets/images/componentesInternos/Ventilador 120mm ARGB.png"),
            ("HDD Seagate 1TB", "assets/images/componentesInternos/HDD Seagate 1TB  .png"),
            ("PSU 600W", "assets/images/componentesInternos/Fuente de poder 600W.png"),
            ("DVD SATA", "assets/images/componentesInternos/dvdsata.png"),
        ]

        card_width_common, card_height_common = 180, 175
        y_offset_common = 130
        for i, (name, image_path) in enumerate(common_internal):
            x = 30 + (i % 5) * (card_width_common + 10)
            y = y_offset_common
            rect = pygame.Rect(x, y, card_width_common, card_height_common)
            card = ComponentCard(name, image_path, "common", rect)
            self.internal_components.append(card)
        
        card_width_desktop, card_height_desktop = 180, 175
        y_offset_desktop_title = y_offset_common + card_height_common + 25
        y_offset_desktop_cards = y_offset_desktop_title + 30 + 15
        for i, (name, image_path) in enumerate(desktop_only):
            row = i // 4
            col = i % 4
            x = (self.width - (4 * card_width_desktop + 3 * 10)) // 2 + col * (card_width_desktop + 10) if row == 0 else \
                (self.width - (3 * card_width_desktop + 2 * 10)) // 2 + col * (card_width_desktop + 10)
            y = y_offset_desktop_cards + row * (card_height_desktop + 15)
            rect = pygame.Rect(x, y, card_width_desktop, card_height_desktop)
            card = ComponentCard(name, image_path, "desktop", rect)
            self.internal_components.append(card)

        # Componentes externos - Tarjetas más grandes y mejor espaciadas
        self.external_components = []
        external_list = [
            ("Monitor LED 24\"", "assets/images/componentesExternos/monitorNew.png"),
            ("Teclado Mecanico", "assets/images/componentesExternos/Teclado mecánico RGB.png"),
            ("Mouse Razen", "assets/images/componentesExternos/mouse.png"),
            ("Bocinas Estereo", "assets/images/componentesExternos/bocinas.png"),
            ("Webcam HD 1080p", "assets/images/componentesExternos/camara.png"),
            ("Microfono USB", "assets/images/componentesExternos/microfono.png"),
            ("UPS", "assets/images/componentesExternos/ups.png"),
            ("HUB USB", "assets/images/componentesExternos/HUB.png"),
        ]
        # Nuevas dimensiones para tarjetas externas
        card_width_external, card_height_external = 220, 200 # Más altas y anchas
        y_offset_external_title = 90
        y_offset_external_cards = y_offset_external_title + 30 + 20 # Título + padding
        
        # Layout de 2 filas x 4 columnas para externos, centrado
        num_cols_external = 4
        total_width_external = num_cols_external * card_width_external + (num_cols_external - 1) * 15 # 15px de espacio
        start_x_external = (self.width - total_width_external) // 2

        for i, (name, image_path) in enumerate(external_list):
            row = i // num_cols_external
            col = i % num_cols_external
            x = start_x_external + col * (card_width_external + 15)
            y = y_offset_external_cards + row * (card_height_external + 20) # Más espacio vertical
            rect = pygame.Rect(x, y, card_width_external, card_height_external)
            card = ComponentCard(name, image_path, "external", rect)
            self.external_components.append(card)
    
    def setup_navigation_buttons(self):
        """Configura los botones de navegación para la ventana más pequeña (970x810)"""
        self.back_button = pygame.Rect(20, 20, 70, 30)
        btn_width, btn_height = 200, 40 # Botones más anchos y un poco más altos

        if self.show_internal:
            # Y pos based on desktop components (2 rows) + spacing
            # Last desktop card ends at: y_offset_desktop_cards + 2*card_height_desktop + 1*15
            # Example: 340 + 2*175 + 15 = 340 + 350 + 15 = 705
            nav_button_y = self.height - 60 # 60px from bottom
            self.finish_button = pygame.Rect((self.width // 2) - btn_width - 10, nav_button_y, btn_width, btn_height)
            self.switch_button = pygame.Rect((self.width // 2) + 10, nav_button_y, btn_width, btn_height)
        else:
            # Y pos based on external components (2 rows) + spacing
            # Last external card ends at: y_offset_external_cards + 2*card_height_external + 1*15
            # Example: 130 + 2*180 + 15 = 130 + 360 + 15 = 505
            nav_button_y = self.height - 60 # 60px from bottom, should be enough space
            self.finish_button = pygame.Rect((self.width // 2) - btn_width - 10, nav_button_y, btn_width, btn_height)
            self.switch_button = pygame.Rect((self.width // 2) + 10, nav_button_y, btn_width, btn_height)
    
    def draw_category_header(self, text, y_pos, width=340): # Ancho por defecto más grande
        """Dibuja el encabezado de una categoría, centrado y con ancho adaptable"""
        # Si el texto es muy largo, la fuente del título de categoría podría reducirse o el ancho del header ajustarse
        # Por ahora, mantenemos la fuente y ajustamos el ancho del header
        actual_text_width = self.category_font.render(text, True, self.category_text).get_width()
        if actual_text_width + 20 > width: # 20px padding
            width = actual_text_width + 30 # Ajustar el ancho del rectángulo del header

        rect = pygame.Rect((self.width - width) // 2, y_pos, width, 30)
        pygame.draw.rect(self.screen, self.category_bg, rect, border_radius=5)
        
        category_text_render = self.category_font.render(text, True, self.category_text)
        text_rect = category_text_render.get_rect(center=rect.center)
        self.screen.blit(category_text_render, text_rect)
    
    def draw_component_card(self, card):
        """Dibuja una tarjeta de componente con espaciado mejorado y estado de bloqueo"""
        is_disabled = (self.computer_type == "laptop" and card.category == "desktop" and self.show_internal)
        
        # Color de fondo según selección o estado deshabilitado
        if is_disabled:
            bg_color = self.disabled_color
        elif card.selected:
            bg_color = self.selected_color
        else:
            bg_color = self.card_color
        
        # Sombra
        shadow_rect = card.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(self.screen, (200, 200, 200), shadow_rect, border_radius=8)
        
        # Tarjeta principal
        pygame.draw.rect(self.screen, bg_color, card.rect, border_radius=8)
        border_color = (150,150,150) if is_disabled else (200,200,200)
        pygame.draw.rect(self.screen, border_color, card.rect, 2, border_radius=8)

        # Imagen del componente (atenuada si está deshabilitada)
        img_to_draw = card.image.copy()
        if is_disabled:
            img_to_draw.set_alpha(100) # Atenuar imagen
        img_x = card.rect.x + (card.rect.width - img_to_draw.get_width()) // 2
        img_y = card.rect.y + 10
        self.screen.blit(img_to_draw, (img_x, img_y))

        # Texto del componente
        if is_disabled:
            text_color = self.disabled_text_color
        elif card.selected:
            text_color = (255,255,255)
        else:
            text_color = self.text_color
            
        font_to_use = self.component_font
        name_text_render = font_to_use.render(card.name, True, text_color)
        if name_text_render.get_width() > card.rect.width - 10:
            smaller_font = pygame.font.Font(None, 14)
            name_text_render = smaller_font.render(card.name, True, text_color)
        
        text_y_center = card.rect.y + card.image.get_height() + 10 + 15
        name_rect = name_text_render.get_rect(center=(card.rect.centerx, text_y_center))
        self.screen.blit(name_text_render, name_rect)

        # Botón (deshabilitado si es necesario)
        if is_disabled:
            button_color = self.disabled_color
            button_text_str = "No disponible"
            pygame.draw.rect(self.screen, button_color, card.button_rect, border_radius=5)
            pygame.draw.rect(self.screen, self.disabled_text_color, card.button_rect, 1, border_radius=5) # Borde tenue
        elif card.selected:
            button_color = (220, 38, 38)
            button_text_str = "Quitar"
            pygame.draw.rect(self.screen, button_color, card.button_rect, border_radius=5)
        else:
            button_color = self.button_color
            button_text_str = "Seleccionar"
            pygame.draw.rect(self.screen, button_color, card.button_rect, border_radius=5)
        
        btn_text_color = self.disabled_text_color if is_disabled else (255,255,255)
        btn_text_render = self.button_font.render(button_text_str, True, btn_text_color)
        btn_text_rect = btn_text_render.get_rect(center=card.button_rect.center)
        self.screen.blit(btn_text_render, btn_text_rect)
    
    def draw_navigation_buttons(self):
        """Dibuja los botones de navegación con texto más grande y corto"""
        pygame.draw.rect(self.screen, (107, 114, 128), self.back_button, border_radius=5)
        back_text_render = self.button_font.render("< Atras", True, (255, 255, 255))
        back_rect = back_text_render.get_rect(center=self.back_button.center)
        self.screen.blit(back_text_render, back_rect)
        
        self.setup_navigation_buttons() 
        
        nav_btn_font = self.category_font 

        finish_text_str = "Continuar Ensamble"
        switch_text_str = "Est. Externos" if self.show_internal else "Est. Internos"

        pygame.draw.rect(self.screen, self.button_color, self.finish_button, border_radius=5)
        finish_text_render = nav_btn_font.render(finish_text_str, True, (255, 255, 255))
        finish_rect = finish_text_render.get_rect(center=self.finish_button.center)
        self.screen.blit(finish_text_render, finish_rect)
        
        pygame.draw.rect(self.screen, self.button_color, self.switch_button, border_radius=5)
        switch_text_render = nav_btn_font.render(switch_text_str, True, (255, 255, 255))
        switch_rect = switch_text_render.get_rect(center=self.switch_button.center)
        self.screen.blit(switch_text_render, switch_rect)

    def draw(self):
        """Renderiza la pantalla completa con ajustes para ventana 970x810"""
        self.screen.fill(self.bg_color)
        title_main_width = 400 # Ancho reducido para título principal
        title_main_height = 35

        # Dibujar indicador de tipo de PC
        pygame.draw.rect(self.screen, self.type_indicator_bg, self.type_indicator_rect, border_radius=5)
        self.screen.blit(self.type_indicator_surface, 
                         (self.type_indicator_rect.x + 10, 
                          self.type_indicator_rect.y + 5))

        if self.show_internal:
            title_rect = pygame.Rect((self.width - title_main_width) // 2, 20, title_main_width, title_main_height)
            pygame.draw.rect(self.screen, self.button_color, title_rect, border_radius=5)
            title_text_render = self.title_font.render("Componentes Internos", True, (255, 255, 255))
            title_text_rect = title_text_render.get_rect(center=title_rect.center)
            self.screen.blit(title_text_render, title_text_rect)
            
            self.draw_category_header("Comunes Laptop/Desktop", 90, width=360)
            # y_offset_common es 130
            self.draw_category_header("Solo para Desktop", 320) # y_offset_desktop_title es aprox 305. Esto es 305+30(h)+15=350 para y_offset_desktop_cards
                                                               # Esto debe ser y_offset_common + card_height_common + 15 = 130+175+15 = 320 (para el título)
        else:
            title_rect = pygame.Rect((self.width - title_main_width) // 2, 20, title_main_width, title_main_height)
            pygame.draw.rect(self.screen, self.button_color, title_rect, border_radius=5)
            title_text_render = self.title_font.render("Componentes Externos", True, (255, 255, 255))
            title_text_rect = title_text_render.get_rect(center=title_rect.center)
            self.screen.blit(title_text_render, title_text_rect)
            
            self.draw_category_header("Perifericos Laptop/Desktop", 90, width=360)
            # y_offset_external_cards es 130

        # Dibujar componentes después de los títulos de categoría
        components_to_draw = self.internal_components if self.show_internal else self.external_components
        for card in components_to_draw:
            self.draw_component_card(card)
        
        self.draw_navigation_buttons()
        if self.dialog:
            self.dialog.draw()
        pygame.display.flip()

    def has_selections(self):
        """Verifica si hay componentes seleccionados"""
        for card in self.internal_components + self.external_components:
            if card.selected:
                return True
        return False
    
    def clear_selections(self):
        """Limpia todas las selecciones"""
        for card in self.internal_components + self.external_components:
            card.selected = False
    
    def handle_component_click(self, pos):
        """Maneja clics en componentes, respetando el estado de bloqueo"""
        components = self.internal_components if self.show_internal else self.external_components
        
        for card in components:
            # Verificar si el componente está bloqueado
            is_disabled = (self.computer_type == "laptop" and card.category == "desktop" and self.show_internal)
            if is_disabled:
                continue # Saltar si está deshabilitado

            if card.button_rect.collidepoint(pos):
                card.selected = not card.selected
                if card.selected:
                    print(f"Componente seleccionado: {card.name}")
                else:
                    print(f"Componente deseleccionado: {card.name}")
                return True
        return False
    
    def show_confirmation_dialog(self, message):
        """Muestra diálogo de confirmación"""
        self.dialog = ConfirmDialog(self.screen, message)
    
    def show_alert(self, message):
        """Muestra un diálogo de alerta simple."""
        self.dialog = ConfirmDialog(self.screen, message, is_alert=True)

    def run(self):
        """Maneja eventos y lógica principal"""
        running = True
        go_back = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    go_back = False 
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.dialog:
                        result = self.dialog.handle_click(event.pos)
                        if self.dialog.is_alert:
                            if result: # Si se hizo clic en OK
                                self.dialog = None # Cerrar alerta
                        else: # Es un diálogo de confirmación
                            if result is True:  
                                self.clear_selections()
                                self.dialog = None
                                if hasattr(self, 'pending_action') and self.pending_action == 'back':
                                    go_back = True
                                    running = False
                                if hasattr(self, 'pending_action'): delattr(self, 'pending_action')
                            elif result is False: 
                                self.dialog = None
                                if hasattr(self, 'pending_action'):
                                    delattr(self, 'pending_action')
                    else:
                        if self.back_button.collidepoint(event.pos):
                            if self.has_selections(): 
                                self.pending_action = 'back' 
                                self.show_confirmation_dialog("Tienes componentes seleccionados.\n¿Descartar cambios y retroceder?")
                            else:
                                go_back = True 
                                running = False
                        elif self.switch_button.collidepoint(event.pos):
                            self.show_internal = not self.show_internal
                        elif self.finish_button.collidepoint(event.pos):
                            # Validaciones para el botón "Continuar Ensamble"
                            selected_internals = [card for card in self.internal_components if card.selected]
                            selected_externals = [card for card in self.external_components if card.selected]

                            # 1. Verificar si hay selección en el ESTANTE ACTUAL
                            current_shelf_components = self.internal_components if self.show_internal else self.external_components
                            has_current_shelf_selection = any(card.selected for card in current_shelf_components)

                            if not has_current_shelf_selection:
                                shelf_name = "internos" if self.show_internal else "externos"
                                self.show_alert(f"Debes seleccionar al menos un\ncomponente del estante de\ncomponentes {shelf_name} para continuar.")
                            # 2. Si hay selección en el estante actual, VERIFICAR EL OTRO ESTANTE
                            elif not selected_internals:
                                self.show_alert("Debes seleccionar al menos un\ncomponente del estante de\ncomponentes INTERNOS para continuar.")
                            elif not selected_externals:
                                self.show_alert("Debes seleccionar al menos un\ncomponente del estante de\ncomponentes EXTERNOS para continuar.")
                            # 3. Si TODO OK, se puede continuar
                            else:
                                final_selected_names = [card.name for card in selected_internals + selected_externals]
                                print(f"Boton 'Continuar Ensamble' presionado. Todos los componentes requeridos seleccionados: {final_selected_names}")
                                # Aquí iría la lógica para pasar a la siguiente fase del ensamble.
                                # Por ahora, podemos hacer que regrese a la pantalla de selección para simular que se completó esta etapa.
                                # go_back = True
                                # running = False
                        else:
                            self.handle_component_click(event.pos)
            
            self.draw()
        
        return go_back