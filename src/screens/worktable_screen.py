import pygame

# --- Colores y Fuentes (pueden moverse a un archivo de configuración después) ---
BG_COLOR = (229, 231, 235)  # Gris claro de fondo
TITLE_BG_COLOR = (59, 130, 246) # Azul para título principal
TITLE_TEXT_COLOR = (255, 255, 255)
SIDEBAR_BG_COLOR = (243, 244, 246) # Gris muy claro para sidebar
SIDEBAR_TITLE_COLOR = (37, 99, 235)
MINI_CARD_BG = (255, 255, 255)
MINI_CARD_BORDER = (209, 213, 219)
MINI_CARD_TEXT_COLOR = (17, 24, 39)
LAPTOP_CHASSIS_COLOR = (209, 213, 219) # Gris para el chasis de la laptop
LAPTOP_SCREEN_AREA_COLOR = (107, 114, 128) # Gris más oscuro para área de pantalla
SLOT_OUTLINE_COLOR = (156, 163, 175) # Borde para los slots
SLOT_FILL_COLOR_EMPTY = (220, 220, 220, 180) # Relleno cuando está vacío
SLOT_FILL_COLOR_HOVER = (187, 247, 208, 200) # Verde para hover correcto
SLOT_TEXT_COLOR = (55, 65, 81)
BUTTON_COLOR = (0, 122, 255)  # Azul para botones
BUTTON_HOVER_COLOR = (0, 80, 170) # Azul más oscuro para hover
BUTTON_TEXT_COLOR = (255, 255, 255)
ALERT_BG_COLOR = (0, 0, 0, 180) # Fondo oscuro semi-transparente para alerta
ALERT_TEXT_COLOR = (255, 255, 255)
ALERT_BOX_COLOR = (75, 75, 75) # Color del recuadro de la alerta

pygame.font.init() # Asegurar que las fuentes estén inicializadas
TITLE_FONT = pygame.font.Font(None, 30)
SIDEBAR_FONT = pygame.font.Font(None, 26)
MINI_CARD_FONT = pygame.font.Font(None, 18) # Un poco más grande para el nombre en la tarjeta
SLOT_NAME_FONT = pygame.font.Font(None, 20) # Para el nombre del slot (RAM, CPU)
BUTTON_FONT = pygame.font.Font(None, 22)
ALERT_FONT = pygame.font.Font(None, 28)
ALERT_MESSAGE_FONT = pygame.font.Font(None, 24)

class MiniCardComponent:
    """Representa un componente arrastrable que se mueve de la sidebar a un slot."""
    def __init__(self, id_name, display_name, image_path, initial_pos_in_sidebar, target_slot_id, card_size=(170, 95), image_render_size=(80,60)):
        self.id_name = id_name
        self.display_name = display_name
        self.image_original = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image_original, image_render_size)
        
        self.card_width, self.card_height = card_size
        self.rect = pygame.Rect(initial_pos_in_sidebar[0], initial_pos_in_sidebar[1], self.card_width, self.card_height)
        
        self.initial_pos_in_sidebar = initial_pos_in_sidebar
        self.target_slot_id = target_slot_id
        
        self.is_dragging = False
        self.is_placed = False # True si está en un slot, False si está en la sidebar (o siendo arrastrada desde ella)
        self.current_slot_id = None # Guarda el ID del slot si está colocada
        self.offset_x = 0
        self.offset_y = 0

    def draw(self, screen):
        # La tarjeta se dibuja en su self.rect actual (sea en sidebar, arrastrada, o en slot)
        pygame.draw.rect(screen, MINI_CARD_BG, self.rect, border_radius=6)
        pygame.draw.rect(screen, MINI_CARD_BORDER, self.rect, 1, border_radius=6)
        
        img_rect = self.image.get_rect(centerx=self.rect.centerx, top=self.rect.top + 8)
        screen.blit(self.image, img_rect)
        
        text_surf = MINI_CARD_FONT.render(self.display_name, True, MINI_CARD_TEXT_COLOR)
        text_rect = text_surf.get_rect(centerx=self.rect.centerx, bottom=self.rect.bottom - 8)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event, worktable_slots):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                # Si se hace clic en una tarjeta (esté en sidebar o en un slot)
                self.is_dragging = True
                self.offset_x = self.rect.x - event.pos[0]
                self.offset_y = self.rect.y - event.pos[1]
                
                # Si estaba colocada, quitarla del slot actual
                if self.is_placed and self.current_slot_id:
                    for slot in worktable_slots:
                        if slot.id_name == self.current_slot_id:
                            slot.remove_component()
                            break
                    self.is_placed = False
                    self.current_slot_id = None
                return True 

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging:
                self.is_dragging = False
                placed_in_slot = False
                for slot in worktable_slots:
                    if slot.id_name == self.target_slot_id and slot.rect.colliderect(self.rect) and not slot.is_occupied():
                        self.rect.center = slot.rect.center
                        self.is_placed = True
                        self.current_slot_id = slot.id_name
                        slot.place_component(self.id_name)
                        print(f"Componente {self.display_name} colocado en slot {slot.display_name_on_slot}")
                        placed_in_slot = True
                        break
                
                if not placed_in_slot:
                    # Si no se colocó en un slot válido, o el slot estaba ocupado, o no era el correcto,
                    # regresa a su posición inicial en la sidebar.
                    self.rect.topleft = self.initial_pos_in_sidebar
                    self.is_placed = False # Asegurar que se marca como no colocada si regresa a sidebar
                    self.current_slot_id = None
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.rect.x = event.pos[0] + self.offset_x
                self.rect.y = event.pos[1] + self.offset_y
                return True
        return False

class DropSlot:
    """Representa una ranura en el esquema de la laptop."""
    def __init__(self, id_name, display_name_on_slot, rect_on_laptop_scheme, accepted_component_id):
        self.id_name = id_name
        self.display_name_on_slot = display_name_on_slot # Texto que se muestra en la ranura (RAM, CPU)
        self.rect = rect_on_laptop_scheme
        self.accepted_component_id = accepted_component_id # El id_name de la MiniCardComponent que acepta
        self.occupied_by_component_id = None

    def is_occupied(self):
        return self.occupied_by_component_id is not None

    def place_component(self, component_id):
        self.occupied_by_component_id = component_id

    def remove_component(self):
        self.occupied_by_component_id = None

    def draw(self, screen, is_hovering_with_correct_item=False):
        current_fill = SLOT_FILL_COLOR_EMPTY
        if is_hovering_with_correct_item and not self.is_occupied():
            current_fill = SLOT_FILL_COLOR_HOVER
        
        slot_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        slot_surface.fill(current_fill)
        screen.blit(slot_surface, self.rect.topleft)

        if not self.is_occupied(): # Solo mostrar nombre del slot si está vacío
            text_surf = SLOT_NAME_FONT.render(self.display_name_on_slot, True, SLOT_TEXT_COLOR)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)
            
        pygame.draw.rect(screen, SLOT_OUTLINE_COLOR, self.rect, 1, border_radius=4)

class WorktableScreen:
    """Pantalla de la mesa de trabajo con un esquema de Laptop dibujado."""
    def __init__(self, screen, computer_type, selected_component_names):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.computer_type = computer_type
        # Guardamos una copia para poder devolverla intacta si se presiona "Atrás"
        self.initial_selected_components = list(selected_component_names) 
        self.selected_component_names = selected_component_names # Esta lista podría modificarse si permitimos quitar componentes

        self.laptop_scheme_width = self.width * 0.65
        self.laptop_scheme_height = self.height * 0.85 # Un poco más alto el chasis
        self.laptop_scheme_rect = pygame.Rect(
            30, 
            (self.height - self.laptop_scheme_height) // 2 + 10, 
            self.laptop_scheme_width,
            self.laptop_scheme_height
        )

        self.sidebar_width = self.width * 0.3 - 50
        self.sidebar_x_start = self.width - self.sidebar_width - 10

        self.slots = []
        self.mini_cards = [] # Todas las mini-tarjetas, estén en sidebar o en slot
        self.currently_dragged_card = None

        self._setup_laptop_scheme_and_components()

        # Botones y Alerta
        self.show_alert = False
        self.alert_message = "Por favor arrastre todas las tarjetas para continuar"
        
        button_width, button_height = 120, 35
        self.back_button_rect = pygame.Rect(20, 20, button_width, button_height)
        self.continue_button_rect = pygame.Rect(
            self.width - button_width - 20, 
            self.height - button_height - 20, 
            button_width, 
            button_height
        )
        
        self.alert_box_rect = pygame.Rect(0, 0, 400, 100) # Se centrará en draw

    def _setup_laptop_scheme_and_components(self):
        # El tamaño de los slots DEBE ser igual al de las MiniCardComponent
        mini_card_w, mini_card_h = 170, 95 # Tamaño actual de mini-tarjeta
        img_in_card_w, img_in_card_h = 80, 60 # Tamaño de imagen dentro de la mini-tarjeta

        # Coordenadas ajustadas para un espaciado óptimo basado en la imagen de referencia
        padding_chasis = 40 
        slot_area_width = self.laptop_scheme_rect.width - 2 * padding_chasis
        slot_area_height = self.laptop_scheme_rect.height - 2 * padding_chasis

        # Coordenadas reorganizadas para evitar superposiciones con mejor espaciado horizontal
        slot_data = [
            # Fila superior - mejor espaciado horizontal uniforme
            # DVD: Parte superior izquierda
            ("SLOT_DVD", "DVD", 
             (padding_chasis + 5, slot_area_height * 0.05, mini_card_w, mini_card_h), 
             "DVD_1"),
            
            # Cooler: Parte superior centro con más separación
            ("SLOT_COOLER", "Cooler", 
             (slot_area_width * 0.42, slot_area_height * 0.05, mini_card_w, mini_card_h), 
             "COOLER_1"),
            
            # RAM: Parte superior derecha con espaciado uniforme
            ("SLOT_RAM", "RAM", 
             (slot_area_width * 0.78, slot_area_height * 0.05, mini_card_w, mini_card_h), 
             "RAM_1"),
            
            # Fila media-superior - mejor espaciado uniforme
            # CPU: Izquierda, debajo del DVD
            ("SLOT_CPU", "CPU", 
             (padding_chasis + 5, slot_area_height * 0.25, mini_card_w, mini_card_h), 
             "CPU_1"),
            
            # M.2: Centro, debajo del Cooler con más separación
            ("SLOT_M2", "M.2", 
             (slot_area_width * 0.42, slot_area_height * 0.25, mini_card_w, mini_card_h), 
             "M2_1"),
            
            # Wi-Fi: Derecha, debajo de la RAM con espaciado uniforme
            ("SLOT_WIFI", "Wi-Fi", 
             (slot_area_width * 0.78, slot_area_height * 0.25, mini_card_w, mini_card_h), 
             "WIFI_1"),
            
            # Fila media - mejor espaciado uniforme
            # GPU: Izquierda, centro vertical
            ("SLOT_GPU", "GPU", 
             (padding_chasis + 5, slot_area_height * 0.45, mini_card_w, mini_card_h), 
             "GPU_1"),
            
            # SSD: Centro con más separación
            ("SLOT_SSD", "SSD", 
             (slot_area_width * 0.42, slot_area_height * 0.45, mini_card_w, mini_card_h), 
             "SSD_1"),
            
            # Ventilador: Derecha con espaciado uniforme
            ("SLOT_FAN", "Ventilador", 
             (slot_area_width * 0.78, slot_area_height * 0.45, mini_card_w, mini_card_h), 
             "FAN_1"),
            
            # Fila inferior - mismo espaciado uniforme que las otras filas
            # HDD: Izquierda inferior
            ("SLOT_HDD", "HDD", 
             (padding_chasis + 5, slot_area_height * 0.70, mini_card_w, mini_card_h), 
             "HDD_1"),
            
            # PSU: Centro inferior con mismo espaciado
            ("SLOT_PSU", "PSU", 
             (slot_area_width * 0.42, slot_area_height * 0.70, mini_card_w, mini_card_h), 
             "PSU_1"),
        ]

        self.slots = [] # Limpiar slots antes de recrearlos
        for id_name, display_name, rel_coords, accepted_id in slot_data:
            abs_rect = pygame.Rect(
                self.laptop_scheme_rect.left + rel_coords[0],
                self.laptop_scheme_rect.top + rel_coords[1],
                rel_coords[2], # Usar mini_card_w directamente
                rel_coords[3]  # Usar mini_card_h directamente
            )
            self.slots.append(DropSlot(id_name, display_name, abs_rect, accepted_id))

        laptop_component_defs = [
            {"id": "RAM_1", "name": "RAM DDR4 8GB", "img": "assets/images/componentesInternos/ram.png", "slot": "SLOT_RAM"},
            {"id": "CPU_1", "name": "Ryzen 7 5700X", "img": "assets/images/componentesInternos/cpu.png", "slot": "SLOT_CPU"},
            {"id": "M2_1", "name": "M.2 NVMe SSD", "img": "assets/images/componentesInternos/m.2.png", "slot": "SLOT_M2"},
            {"id": "SSD_1", "name": "Kingston SSD 1TB", "img": "assets/images/componentesInternos/ssd.png", "slot": "SLOT_SSD"},
            {"id": "WIFI_1", "name": "Modulo Wi-Fi/BT", "img": "assets/images/componentesInternos/módulo Wi-Fi:Bluetooth.png", "slot": "SLOT_WIFI"}
        ]

        sidebar_item_y = 100
        sidebar_item_spacing = 10
        self.mini_cards = [] # Limpiar antes de recrear
        for comp_def in laptop_component_defs:
            if comp_def["name"] in self.selected_component_names:
                pos_x = self.sidebar_x_start + (self.sidebar_width - mini_card_w) // 2
                pos_y = sidebar_item_y
                mini_card = MiniCardComponent(
                    comp_def["id"], comp_def["name"], comp_def["img"],
                    (pos_x, pos_y), comp_def["slot"], 
                    card_size=(mini_card_w, mini_card_h), 
                    image_render_size=(img_in_card_w, img_in_card_h)
                )
                self.mini_cards.append(mini_card)
                sidebar_item_y += mini_card.card_height + sidebar_item_spacing

    def run(self):
        running = True
        clock = pygame.time.Clock()
        action_to_return = {"action": "back_to_selection", "selected_components": self.initial_selected_components} # Valor por defecto

        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    action_to_return = {"action": "quit"}
                    break # Salir del bucle de eventos

                if self.show_alert:
                    if event.type == pygame.MOUSEBUTTONDOWN: # Ocultar alerta con cualquier clic
                        self.show_alert = False
                    continue # No procesar más eventos si la alerta está activa y se hizo clic

                # Manejo de eventos para los botones primero
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button_rect.collidepoint(mouse_pos):
                        running = False
                        action_to_return = {"action": "back_to_selection", "selected_components": self.initial_selected_components}
                        break 
                    
                    elif self.continue_button_rect.collidepoint(mouse_pos):
                        all_placed = True
                        if not self.mini_cards: # Si no hay tarjetas para colocar
                            all_placed = True
                        else:
                            for card in self.mini_cards:
                                if not card.is_placed:
                                    all_placed = False
                                    break
                        
                        if all_placed:
                            print("Todos los componentes colocados. Procediendo...")
                            running = False
                            action_to_return = {"action": "assembly_complete"} # O el siguiente paso
                            break
                        else:
                            self.show_alert = True
                            print("Alerta: Faltan componentes por colocar.")
                        # No 'break' aquí para que el resto de la lógica de arrastre no se salte si se muestra la alerta

                # Lógica de arrastrar y soltar tarjetas
                if not self.show_alert : # Solo procesar arrastre si la alerta no está visible
                    if self.currently_dragged_card:
                        if self.currently_dragged_card.handle_event(event, self.slots):
                            if not self.currently_dragged_card.is_dragging:
                                self.currently_dragged_card = None
                            # No 'continue' aquí necesariamente, podría haber otros eventos.
                            # El 'handle_event' de la tarjeta devuelve True si manejó el evento.

                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # No es 'else', es independiente
                        for card in self.mini_cards:
                            if card.rect.collidepoint(mouse_pos):
                                can_drag_this = True
                                if not card.is_placed:
                                    for slot_check in self.slots:
                                        if slot_check.id_name == card.target_slot_id and slot_check.is_occupied():
                                            can_drag_this = False
                                            break
                                if can_drag_this:
                                    if card.handle_event(event, self.slots):
                                        self.currently_dragged_card = card
                                        break 
            if not running: # Si un botón causó la salida, salir del bucle principal
                break

            self.draw(mouse_pos)
            pygame.display.flip()
            clock.tick(60)
        
        return action_to_return

    def draw(self, mouse_pos):
        self.screen.fill(BG_COLOR)
        
        # Dibujar el chasis principal de la laptop
        pygame.draw.rect(self.screen, LAPTOP_CHASSIS_COLOR, self.laptop_scheme_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100,100,100), self.laptop_scheme_rect, 3, border_radius=15)
        
        # Agregar tornillos en las esquinas (círculos pequeños)
        screw_radius = 4
        screw_color = (80, 80, 80)  # Gris oscuro para los tornillos
        screw_offset = 15  # Distancia desde la esquina
        
        # Tornillo esquina superior izquierda
        pygame.draw.circle(self.screen, screw_color, 
                          (self.laptop_scheme_rect.left + screw_offset, 
                           self.laptop_scheme_rect.top + screw_offset), screw_radius)
        
        # Tornillo esquina superior derecha
        pygame.draw.circle(self.screen, screw_color, 
                          (self.laptop_scheme_rect.right - screw_offset, 
                           self.laptop_scheme_rect.top + screw_offset), screw_radius)
        
        # Tornillo esquina inferior izquierda
        pygame.draw.circle(self.screen, screw_color, 
                          (self.laptop_scheme_rect.left + screw_offset, 
                           self.laptop_scheme_rect.bottom - screw_offset), screw_radius)
        
        # Tornillo esquina inferior derecha
        pygame.draw.circle(self.screen, screw_color, 
                          (self.laptop_scheme_rect.right - screw_offset, 
                           self.laptop_scheme_rect.bottom - screw_offset), screw_radius)
        
        # Área de pantalla
        screen_area_rect = pygame.Rect(self.laptop_scheme_rect.x + 20, self.laptop_scheme_rect.y + 20, self.laptop_scheme_rect.width - 40, self.laptop_scheme_rect.height * 0.1)
        pygame.draw.rect(self.screen, LAPTOP_SCREEN_AREA_COLOR, screen_area_rect, border_radius=5)

        for slot in self.slots:
            is_hovering_correct = False
            if self.currently_dragged_card and \
               self.currently_dragged_card.target_slot_id == slot.id_name and \
               slot.rect.collidepoint(mouse_pos):
                is_hovering_correct = True
            slot.draw(self.screen, is_hovering_correct)

        sidebar_display_rect = pygame.Rect(self.sidebar_x_start, 0, self.sidebar_width, self.height)
        pygame.draw.rect(self.screen, SIDEBAR_BG_COLOR, sidebar_display_rect)
        pygame.draw.line(self.screen, MINI_CARD_BORDER, (self.sidebar_x_start, 0), (self.sidebar_x_start, self.height), 2)
        sidebar_title_surface = SIDEBAR_FONT.render("Componentes", True, SIDEBAR_TITLE_COLOR)
        sidebar_title_rect = sidebar_title_surface.get_rect(centerx=sidebar_display_rect.centerx, top=sidebar_display_rect.top + 40)
        self.screen.blit(sidebar_title_surface, sidebar_title_rect)

        # Dibujar todas las Mini-Tarjetas (su posición es manejada por is_placed y dragging)
        for card in self.mini_cards:
            # Solo dibujar en la sidebar si no está colocada Y no se está arrastrando activamente ELLA MISMA
            # O si se está arrastrando (en cuyo caso su self.rect ya tiene la pos del mouse)
            if not card.is_placed or (self.currently_dragged_card == card and card.is_dragging) :
                 if not card.is_placed and not (self.currently_dragged_card == card and card.is_dragging):
                     card.rect.topleft = card.initial_pos_in_sidebar # Asegurar que está en sidebar si no está colocada ni se arrastra
                 card.draw(self.screen)
            elif card.is_placed and self.currently_dragged_card != card: # Dibujarla en su slot si está colocada y no se está arrastrando
                 card.draw(self.screen)
        
        # El componente arrastrado activamente ya se dibuja por su propio método draw 
        # si está en la lista self.mini_cards y su self.rect se actualiza.

        title_surface = TITLE_FONT.render(f"Mesa de trabajo - {self.computer_type.capitalize()}", True, TITLE_TEXT_COLOR)
        title_bg_width = title_surface.get_width() + 40
        title_bg_rect = pygame.Rect((self.width - title_bg_width) // 2, 20, title_bg_width, 40)
        # Ajustar para que no choque con el botón "Atrás" si el título es muy ancho
        if title_bg_rect.left < self.back_button_rect.right + 10:
            title_bg_rect.left = self.back_button_rect.right + 10
            if title_bg_rect.right > self.width - 20 : # Asegurar que no se salga por la derecha
                 title_bg_rect.right = self.width -20
                 title_bg_rect.width = title_bg_rect.right - title_bg_rect.left


        pygame.draw.rect(self.screen, TITLE_BG_COLOR, title_bg_rect, border_radius=6)
        title_rect = title_surface.get_rect(center=title_bg_rect.center)
        self.screen.blit(title_surface, title_rect)

        # Dibujar botones
        # Botón Atrás
        back_btn_color = BUTTON_HOVER_COLOR if self.back_button_rect.collidepoint(mouse_pos) and not self.show_alert else BUTTON_COLOR
        pygame.draw.rect(self.screen, back_btn_color, self.back_button_rect, border_radius=6)
        back_text_surf = BUTTON_FONT.render("Atrás", True, BUTTON_TEXT_COLOR)
        back_text_rect = back_text_surf.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text_surf, back_text_rect)

        # Botón Continuar
        cont_btn_color = BUTTON_HOVER_COLOR if self.continue_button_rect.collidepoint(mouse_pos) and not self.show_alert else BUTTON_COLOR
        pygame.draw.rect(self.screen, cont_btn_color, self.continue_button_rect, border_radius=6)
        cont_text_surf = BUTTON_FONT.render("Continuar", True, BUTTON_TEXT_COLOR)
        cont_text_rect = cont_text_surf.get_rect(center=self.continue_button_rect.center)
        self.screen.blit(cont_text_surf, cont_text_rect)
        
        # Dibujar Alerta si está activa
        if self.show_alert:
            # Fondo semi-transparente sobre toda la pantalla
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill(ALERT_BG_COLOR)
            self.screen.blit(overlay, (0,0))
            
            # Caja de la alerta
            self.alert_box_rect.center = (self.width // 2, self.height // 2)
            pygame.draw.rect(self.screen, ALERT_BOX_COLOR, self.alert_box_rect, border_radius=10)
            pygame.draw.rect(self.screen, MINI_CARD_BORDER, self.alert_box_rect, 2, border_radius=10) # Borde

            alert_title_surf = ALERT_FONT.render("Alerta", True, ALERT_TEXT_COLOR)
            alert_title_rect = alert_title_surf.get_rect(centerx=self.alert_box_rect.centerx, top=self.alert_box_rect.top + 15)
            self.screen.blit(alert_title_surf, alert_title_rect)
            
            msg_surf = ALERT_MESSAGE_FONT.render(self.alert_message, True, ALERT_TEXT_COLOR)
            msg_rect = msg_surf.get_rect(centerx=self.alert_box_rect.centerx, top=alert_title_rect.bottom + 10)
            self.screen.blit(msg_surf, msg_rect)
            
            dismiss_surf = MINI_CARD_FONT.render("(Haz clic para cerrar)", True, (200,200,200))
            dismiss_rect = dismiss_surf.get_rect(centerx=self.alert_box_rect.centerx, bottom=self.alert_box_rect.bottom -10)
            self.screen.blit(dismiss_surf, dismiss_rect) 


class WorktableDesktopScreen:
    """Pantalla de la mesa de trabajo con un esquema de Desktop/Torre dibujado."""
    def __init__(self, screen, computer_type, selected_component_names):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.computer_type = computer_type
        # Guardamos una copia para poder devolverla intacta si se presiona "Atrás"
        self.initial_selected_components = list(selected_component_names) 
        self.selected_component_names = selected_component_names

        # Hacer la torre un poco más pequeña para dar más espacio al sidebar
        self.desktop_scheme_width = self.width * 0.58  # Reducido de 0.65 a 0.58
        self.desktop_scheme_height = self.height * 0.85
        self.desktop_scheme_rect = pygame.Rect(
            30, 
            (self.height - self.desktop_scheme_height) // 2 + 10, 
            self.desktop_scheme_width,
            self.desktop_scheme_height
        )

        # Más espacio para el sidebar
        self.sidebar_width = self.width * 0.38 - 30  # Aumentado para acomodar más componentes
        self.sidebar_x_start = self.width - self.sidebar_width - 10

        self.slots = []
        self.mini_cards = []
        self.currently_dragged_card = None

        self._setup_desktop_scheme_and_components()

        # Botones y Alerta
        self.show_alert = False
        self.alert_message = "Por favor arrastre todas las tarjetas para continuar"
        
        button_width, button_height = 120, 35
        self.back_button_rect = pygame.Rect(20, 20, button_width, button_height)
        self.continue_button_rect = pygame.Rect(
            self.width - button_width - 20, 
            self.height - button_height - 20, 
            button_width, 
            button_height
        )
        
        self.alert_box_rect = pygame.Rect(0, 0, 400, 100)

    def _setup_desktop_scheme_and_components(self):
        # Tarjetas más pequeñas para acomodar 11 componentes
        mini_card_w, mini_card_h = 140, 80  # Reducido de 170x95 a 140x80
        img_in_card_w, img_in_card_h = 60, 50  # Reducido de 80x60 a 60x50

        # Distribución reorganizada para evitar superposiciones
        padding_chasis = 35 
        slot_area_width = self.desktop_scheme_rect.width - 2 * padding_chasis
        slot_area_height = self.desktop_scheme_rect.height - 2 * padding_chasis

        # Coordenadas reorganizadas para evitar superposiciones con mejor espaciado horizontal
        slot_data = [
            # Fila superior - mejor espaciado horizontal uniforme
            # DVD: Parte superior izquierda
            ("SLOT_DVD", "DVD", 
             (padding_chasis + 5, slot_area_height * 0.05, mini_card_w, mini_card_h), 
             "DVD_1"),
            
            # Cooler: Parte superior centro con más separación
            ("SLOT_COOLER", "Cooler", 
             (slot_area_width * 0.42, slot_area_height * 0.05, mini_card_w, mini_card_h), 
             "COOLER_1"),
            
            # RAM: Parte superior derecha con espaciado uniforme
            ("SLOT_RAM", "RAM", 
             (slot_area_width * 0.78, slot_area_height * 0.05, mini_card_w, mini_card_h), 
             "RAM_1"),
            
            # Fila media-superior - mejor espaciado uniforme
            # CPU: Izquierda, debajo del DVD
            ("SLOT_CPU", "CPU", 
             (padding_chasis + 5, slot_area_height * 0.25, mini_card_w, mini_card_h), 
             "CPU_1"),
            
            # M.2: Centro, debajo del Cooler con más separación
            ("SLOT_M2", "M.2", 
             (slot_area_width * 0.42, slot_area_height * 0.25, mini_card_w, mini_card_h), 
             "M2_1"),
            
            # Wi-Fi: Derecha, debajo de la RAM con espaciado uniforme
            ("SLOT_WIFI", "Wi-Fi", 
             (slot_area_width * 0.78, slot_area_height * 0.25, mini_card_w, mini_card_h), 
             "WIFI_1"),
            
            # Fila media - mejor espaciado uniforme
            # GPU: Izquierda, centro vertical
            ("SLOT_GPU", "GPU", 
             (padding_chasis + 5, slot_area_height * 0.45, mini_card_w, mini_card_h), 
             "GPU_1"),
            
            # SSD: Centro con más separación
            ("SLOT_SSD", "SSD", 
             (slot_area_width * 0.42, slot_area_height * 0.45, mini_card_w, mini_card_h), 
             "SSD_1"),
            
            # Ventilador: Derecha con espaciado uniforme
            ("SLOT_FAN", "Ventilador", 
             (slot_area_width * 0.78, slot_area_height * 0.45, mini_card_w, mini_card_h), 
             "FAN_1"),
            
            # Fila inferior - mismo espaciado uniforme que las otras filas
            # HDD: Izquierda inferior
            ("SLOT_HDD", "HDD", 
             (padding_chasis + 5, slot_area_height * 0.70, mini_card_w, mini_card_h), 
             "HDD_1"),
            
            # PSU: Centro inferior con mismo espaciado
            ("SLOT_PSU", "PSU", 
             (slot_area_width * 0.42, slot_area_height * 0.70, mini_card_w, mini_card_h), 
             "PSU_1"),
        ]

        self.slots = []
        for id_name, display_name, rel_coords, accepted_id in slot_data:
            abs_rect = pygame.Rect(
                self.desktop_scheme_rect.left + rel_coords[0],
                self.desktop_scheme_rect.top + rel_coords[1],
                rel_coords[2],
                rel_coords[3]
            )
            self.slots.append(DropSlot(id_name, display_name, abs_rect, accepted_id))

        # Componentes de Desktop corregidos con DVD SATA
        desktop_component_defs = [
            {"id": "GPU_1", "name": "NVIDIA RTX 3060", "img": "assets/images/componentesInternos/gpu.png", "slot": "SLOT_GPU"},
            {"id": "RAM_1", "name": "RAM DDR4 8GB", "img": "assets/images/componentesInternos/ram.png", "slot": "SLOT_RAM"},
            {"id": "CPU_1", "name": "Ryzen 7 5700X", "img": "assets/images/componentesInternos/cpu.png", "slot": "SLOT_CPU"},
            {"id": "PSU_1", "name": "PSU 600W", "img": "assets/images/componentesInternos/Fuente de poder 600W.png", "slot": "SLOT_PSU"},
            {"id": "HDD_1", "name": "HDD Seagate 1TB", "img": "assets/images/componentesInternos/HDD Seagate 1TB  .png", "slot": "SLOT_HDD"},
            {"id": "WIFI_1", "name": "Modulo Wi-Fi/BT", "img": "assets/images/componentesInternos/módulo Wi-Fi:Bluetooth.png", "slot": "SLOT_WIFI"},
            {"id": "FAN_1", "name": "Ventilador ARGB", "img": "assets/images/componentesInternos/Ventilador 120mm ARGB.png", "slot": "SLOT_FAN"},
            {"id": "M2_1", "name": "M.2 NVMe SSD", "img": "assets/images/componentesInternos/m.2.png", "slot": "SLOT_M2"},
            {"id": "COOLER_1", "name": "Cooler Master H212", "img": "assets/images/componentesInternos/Cooler Master Hyper 212.png", "slot": "SLOT_COOLER"},
            {"id": "SSD_1", "name": "Kingston SSD 1TB", "img": "assets/images/componentesInternos/ssd.png", "slot": "SLOT_SSD"},
            {"id": "DVD_1", "name": "DVD SATA", "img": "assets/images/componentesInternos/dvdsata.png", "slot": "SLOT_DVD"},
        ]

        # Configuración para dos columnas - centradas en el sidebar
        cards_per_column = 7  # Primera columna tendrá 7 componentes
        column_width = mini_card_w + 8  # Ancho de cada columna con un poco más de padding
        
        # Ajustar espaciado para las tarjetas más pequeñas
        sidebar_item_y = 80  # Empezar más arriba
        sidebar_item_spacing = 6  # Menor espaciado entre tarjetas
        
        # Centrar las dos columnas en el sidebar
        total_columns_width = (2 * mini_card_w) + 8  # Ancho total de las dos columnas
        sidebar_center_x = self.sidebar_x_start + (self.sidebar_width // 2)
        first_column_x = sidebar_center_x - (total_columns_width // 2)
        second_column_x = first_column_x + column_width
        
        self.mini_cards = []
        card_index = 0
        
        for comp_def in desktop_component_defs:
            if comp_def["name"] in self.selected_component_names:
                # Determinar en qué columna va este componente
                if card_index < cards_per_column:
                    # Primera columna (7 componentes)
                    pos_x = first_column_x
                    pos_y = sidebar_item_y + (card_index * (mini_card_h + sidebar_item_spacing))
                else:
                    # Segunda columna (4 componentes restantes)
                    pos_x = second_column_x
                    pos_y = sidebar_item_y + ((card_index - cards_per_column) * (mini_card_h + sidebar_item_spacing))
                
                mini_card = MiniCardComponent(
                    comp_def["id"], comp_def["name"], comp_def["img"],
                    (pos_x, pos_y), comp_def["slot"], 
                    card_size=(mini_card_w, mini_card_h), 
                    image_render_size=(img_in_card_w, img_in_card_h)
                )
                self.mini_cards.append(mini_card)
                card_index += 1

    def run(self):
        running = True
        clock = pygame.time.Clock()
        action_to_return = {"action": "back_to_selection", "selected_components": self.initial_selected_components}

        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    action_to_return = {"action": "quit"}
                    break

                if self.show_alert:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.show_alert = False
                    continue

                # Manejo de eventos para los botones
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button_rect.collidepoint(mouse_pos):
                        running = False
                        action_to_return = {"action": "back_to_selection", "selected_components": self.initial_selected_components}
                        break 
                    
                    elif self.continue_button_rect.collidepoint(mouse_pos):
                        all_placed = True
                        if not self.mini_cards:
                            all_placed = True
                        else:
                            for card in self.mini_cards:
                                if not card.is_placed:
                                    all_placed = False
                                    break
                        
                        if all_placed:
                            print("Todos los componentes colocados. Procediendo...")
                            running = False
                            action_to_return = {"action": "assembly_complete"}
                            break
                        else:
                            self.show_alert = True
                            print("Alerta: Faltan componentes por colocar.")

                # Lógica de arrastrar y soltar tarjetas
                if not self.show_alert:
                    if self.currently_dragged_card:
                        if self.currently_dragged_card.handle_event(event, self.slots):
                            if not self.currently_dragged_card.is_dragging:
                                self.currently_dragged_card = None

                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for card in self.mini_cards:
                            if card.rect.collidepoint(mouse_pos):
                                can_drag_this = True
                                if not card.is_placed:
                                    for slot_check in self.slots:
                                        if slot_check.id_name == card.target_slot_id and slot_check.is_occupied():
                                            can_drag_this = False
                                            break
                                if can_drag_this:
                                    if card.handle_event(event, self.slots):
                                        self.currently_dragged_card = card
                                        break 
            if not running:
                break

            self.draw(mouse_pos)
            pygame.display.flip()
            clock.tick(60)
        
        return action_to_return

    def draw(self, mouse_pos):
        self.screen.fill(BG_COLOR)
        
        # Dibujar el chasis principal del Desktop/Torre
        pygame.draw.rect(self.screen, LAPTOP_CHASSIS_COLOR, self.desktop_scheme_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100,100,100), self.desktop_scheme_rect, 3, border_radius=15)
        
        # Agregar tornillos en las esquinas
        screw_radius = 4
        screw_color = (80, 80, 80)
        screw_offset = 15
        
        # Tornillos en las 4 esquinas
        pygame.draw.circle(self.screen, screw_color, 
                          (self.desktop_scheme_rect.left + screw_offset, 
                           self.desktop_scheme_rect.top + screw_offset), screw_radius)
        
        pygame.draw.circle(self.screen, screw_color, 
                          (self.desktop_scheme_rect.right - screw_offset, 
                           self.desktop_scheme_rect.top + screw_offset), screw_radius)
        
        pygame.draw.circle(self.screen, screw_color, 
                          (self.desktop_scheme_rect.left + screw_offset, 
                           self.desktop_scheme_rect.bottom - screw_offset), screw_radius)
        
        pygame.draw.circle(self.screen, screw_color, 
                          (self.desktop_scheme_rect.right - screw_offset, 
                           self.desktop_scheme_rect.bottom - screw_offset), screw_radius)

        # Dibujar representación del motherboard (rectángulo grande en el centro-izquierda)
        motherboard_rect = pygame.Rect(
            self.desktop_scheme_rect.left + 50,  # Ajustado para la torre más pequeña
            self.desktop_scheme_rect.top + 70,   # Ajustado
            self.desktop_scheme_rect.width * 0.55,  # Ajustado proporcionalmente
            self.desktop_scheme_rect.height * 0.65  # Ajustado
        )
        pygame.draw.rect(self.screen, (50, 70, 90), motherboard_rect, border_radius=8)
        pygame.draw.rect(self.screen, (30, 50, 70), motherboard_rect, 2, border_radius=8)
        
        # Texto "MOTHERBOARD" en el centro con fuente más pequeña
        motherboard_font = pygame.font.Font(None, 32)  # Reducido de 36 a 32
        motherboard_text = motherboard_font.render("MOTHERBOARD", True, (200, 200, 200))
        motherboard_text_rect = motherboard_text.get_rect(center=motherboard_rect.center)
        self.screen.blit(motherboard_text, motherboard_text_rect)

        # Dibujar slots
        for slot in self.slots:
            is_hovering_correct = False
            if self.currently_dragged_card and \
               self.currently_dragged_card.target_slot_id == slot.id_name and \
               slot.rect.collidepoint(mouse_pos):
                is_hovering_correct = True
            slot.draw(self.screen, is_hovering_correct)

        # Sidebar
        sidebar_display_rect = pygame.Rect(self.sidebar_x_start, 0, self.sidebar_width, self.height)
        pygame.draw.rect(self.screen, SIDEBAR_BG_COLOR, sidebar_display_rect)
        pygame.draw.line(self.screen, MINI_CARD_BORDER, (self.sidebar_x_start, 0), (self.sidebar_x_start, self.height), 2)
        sidebar_title_surface = SIDEBAR_FONT.render("Componentes", True, SIDEBAR_TITLE_COLOR)
        sidebar_title_rect = sidebar_title_surface.get_rect(centerx=sidebar_display_rect.centerx, top=sidebar_display_rect.top + 40)
        self.screen.blit(sidebar_title_surface, sidebar_title_rect)

        # Dibujar todas las Mini-Tarjetas
        for card in self.mini_cards:
            if not card.is_placed or (self.currently_dragged_card == card and card.is_dragging):
                if not card.is_placed and not (self.currently_dragged_card == card and card.is_dragging):
                    card.rect.topleft = card.initial_pos_in_sidebar
                card.draw(self.screen)
            elif card.is_placed and self.currently_dragged_card != card:
                card.draw(self.screen)

        # Título
        title_surface = TITLE_FONT.render(f"Mesa de trabajo - {self.computer_type.capitalize()}", True, TITLE_TEXT_COLOR)
        title_bg_width = title_surface.get_width() + 40
        title_bg_rect = pygame.Rect((self.width - title_bg_width) // 2, 20, title_bg_width, 40)
        
        if title_bg_rect.left < self.back_button_rect.right + 10:
            title_bg_rect.left = self.back_button_rect.right + 10
            if title_bg_rect.right > self.width - 20:
                title_bg_rect.right = self.width - 20
                title_bg_rect.width = title_bg_rect.right - title_bg_rect.left

        pygame.draw.rect(self.screen, TITLE_BG_COLOR, title_bg_rect, border_radius=6)
        title_rect = title_surface.get_rect(center=title_bg_rect.center)
        self.screen.blit(title_surface, title_rect)

        # Dibujar botones
        # Botón Atrás
        back_btn_color = BUTTON_HOVER_COLOR if self.back_button_rect.collidepoint(mouse_pos) and not self.show_alert else BUTTON_COLOR
        pygame.draw.rect(self.screen, back_btn_color, self.back_button_rect, border_radius=6)
        back_text_surf = BUTTON_FONT.render("Atrás", True, BUTTON_TEXT_COLOR)
        back_text_rect = back_text_surf.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text_surf, back_text_rect)

        # Botón Continuar
        cont_btn_color = BUTTON_HOVER_COLOR if self.continue_button_rect.collidepoint(mouse_pos) and not self.show_alert else BUTTON_COLOR
        pygame.draw.rect(self.screen, cont_btn_color, self.continue_button_rect, border_radius=6)
        cont_text_surf = BUTTON_FONT.render("Continuar", True, BUTTON_TEXT_COLOR)
        cont_text_rect = cont_text_surf.get_rect(center=self.continue_button_rect.center)
        self.screen.blit(cont_text_surf, cont_text_rect)
        
        # Dibujar Alerta si está activa
        if self.show_alert:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill(ALERT_BG_COLOR)
            self.screen.blit(overlay, (0,0))
            
            self.alert_box_rect.center = (self.width // 2, self.height // 2)
            pygame.draw.rect(self.screen, ALERT_BOX_COLOR, self.alert_box_rect, border_radius=10)
            pygame.draw.rect(self.screen, MINI_CARD_BORDER, self.alert_box_rect, 2, border_radius=10)

            alert_title_surf = ALERT_FONT.render("Alerta", True, ALERT_TEXT_COLOR)
            alert_title_rect = alert_title_surf.get_rect(centerx=self.alert_box_rect.centerx, top=self.alert_box_rect.top + 15)
            self.screen.blit(alert_title_surf, alert_title_rect)
            
            msg_surf = ALERT_MESSAGE_FONT.render(self.alert_message, True, ALERT_TEXT_COLOR)
            msg_rect = msg_surf.get_rect(centerx=self.alert_box_rect.centerx, top=alert_title_rect.bottom + 10)
            self.screen.blit(msg_surf, msg_rect)
            
            dismiss_surf = MINI_CARD_FONT.render("(Haz clic para cerrar)", True, (200,200,200))
            dismiss_rect = dismiss_surf.get_rect(centerx=self.alert_box_rect.centerx, bottom=self.alert_box_rect.bottom - 10)
            self.screen.blit(dismiss_surf, dismiss_rect) 