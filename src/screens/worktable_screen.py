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
        # Cargar imagen
        try:
            self.image_original = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image_original, image_render_size)
        except:
            # Crear imagen placeholder si no se puede cargar
            self.image_original = pygame.Surface((100, 100))
            self.image_original.fill((120, 120, 120))
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

        # Coordenadas ajustadas para un espaciado óptimo basado en la imagen de referencia (solo 5 ranuras para laptop)
        padding_chasis = 40 
        slot_area_width = self.laptop_scheme_rect.width - 2 * padding_chasis
        slot_area_height = self.laptop_scheme_rect.height - 2 * padding_chasis

        # Coordenadas reorganizadas para las 5 ranuras de laptop con mejor espaciado y centradas
        slot_data = [
            # RAM: Lado izquierdo, centrado verticalmente
            ("SLOT_RAM", "RAM", 
             (padding_chasis + 10, slot_area_height * 0.45, mini_card_w, mini_card_h), 
             "RAM_1"),
            
            # CPU: Centro-izquierda, arriba del centro
            ("SLOT_CPU", "CPU", 
             (slot_area_width * 0.25, slot_area_height * 0.25, mini_card_w, mini_card_h), 
             "CPU_1"),
            
            # M.2: Superior derecha
            ("SLOT_M2", "M.2", 
             (slot_area_width * 0.60, slot_area_height * 0.20, mini_card_w, mini_card_h), 
             "M2_1"),
            
            # SSD: Centro-derecha, debajo de M.2
            ("SLOT_SSD", "SSD", 
             (slot_area_width * 0.60, slot_area_height * 0.45, mini_card_w, mini_card_h), 
             "SSD_1"),
            
            # Wi-Fi: Inferior derecha
            ("SLOT_WIFI", "Wi-Fi", 
             (slot_area_width * 0.60, slot_area_height * 0.70, mini_card_w, mini_card_h), 
             "WIFI_1"),
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

        # Componentes de laptop (solo los 5 correctos)
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
            dismiss_rect = dismiss_surf.get_rect(centerx=self.alert_box_rect.centerx, bottom=self.alert_box_rect.bottom - 10)
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

        # Crear mini cards para componentes seleccionados distribuidas en dos columnas
        sidebar_item_y = 80
        sidebar_item_spacing = 8
        cards_per_column = 4  # 4 componentes por columna para un total de 8
        column_width = mini_card_w + 10
        
        # Centrar las columnas en el sidebar
        total_columns_width = (2 * mini_card_w) + 10
        sidebar_center_x = self.sidebar_x_start + (self.sidebar_width // 2)
        first_column_x = sidebar_center_x - (total_columns_width // 2)
        second_column_x = first_column_x + column_width
        
        self.mini_cards = []
        card_index = 0
        
        for comp_def in desktop_component_defs:
            if comp_def["name"] in self.selected_component_names:
                # Determinar en qué columna va este componente
                if card_index < cards_per_column:
                    # Primera columna
                    pos_x = first_column_x
                    pos_y = sidebar_item_y + (card_index * (mini_card_h + sidebar_item_spacing))
                else:
                    # Segunda columna
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
                        action_to_return = {"action": "back_to_selection", "selected_components": self.initial_selected_components}
                        running = False
                        break
                    elif self.continue_button_rect.collidepoint(mouse_pos):
                        # Verificar que todos los componentes estén conectados
                        if self._all_components_connected():
                            action_to_return = {"action": "assembly_complete"}
                            running = False
                        else:
                            self.show_alert = True
                        break

                # Lógica de drag & drop usando el sistema existente
                if not self.show_alert:
                    if self.currently_dragged_card:
                        if self.currently_dragged_card.handle_event(event, self.slots):
                            if not self.currently_dragged_card.is_dragging:
                                self.currently_dragged_card = None

                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for card in self.mini_cards:
                            if card.rect.collidepoint(mouse_pos):
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
        sidebar_display_rect = pygame.Rect(self.sidebar_x_start, 60, self.sidebar_width, self.height - 120)
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

    def _all_components_connected(self):
        """Verifica si todos los componentes han sido conectados"""
        return all(card.is_placed for card in self.mini_cards) if self.mini_cards else True


class LaptopExternalConnectionScreen:
    """Pantalla para conectar componentes externos a la laptop."""
    def __init__(self, screen, computer_type, selected_external_components):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.computer_type = computer_type
        self.selected_external_components = selected_external_components

        # Área para la ilustración de laptop (centro, pero un poco a la izquierda)
        self.laptop_illustration_width = self.width * 0.50
        self.laptop_illustration_height = self.height * 0.70
        self.laptop_illustration_rect = pygame.Rect(
            50, 
            (self.height - self.laptop_illustration_height) // 2 + 20, 
            self.laptop_illustration_width,
            self.laptop_illustration_height
        )

        # Área del sidebar para componentes externos (derecha)
        self.sidebar_width = self.width * 0.35
        self.sidebar_x_start = self.width - self.sidebar_width - 10

        self.slots = []
        self.mini_cards = []
        self.currently_dragged_card = None

        self._setup_laptop_external_connections()

        # Botones y Alerta
        self.show_alert = False
        self.alert_message = "Por favor conecte todos los componentes externos para continuar"
        
        button_width, button_height = 120, 35
        self.back_button_rect = pygame.Rect(20, 20, button_width, button_height)
        self.continue_button_rect = pygame.Rect(
            self.width - button_width - 20, 
            self.height - button_height - 20, 
            button_width, 
            button_height
        )
        
        self.alert_box_rect = pygame.Rect(0, 0, 400, 100)

    def _setup_laptop_external_connections(self):
        # Tarjetas para componentes externos
        mini_card_w, mini_card_h = 140, 80
        img_in_card_w, img_in_card_h = 60, 50

        # Hub USB en el centro-izquierda de la laptop para conectar periféricos
        hub_center_x = self.laptop_illustration_rect.centerx - 60  # Movido hacia la derecha (era -80)
        hub_center_y = self.laptop_illustration_rect.centery
        
        # Slots para componentes externos distribuidos alrededor del hub
        slot_data = [
            # Primera fila (arriba)
            # Mouse - Conectado al hub, arriba izquierda
            ("SLOT_MOUSE", "Mouse", 
             (hub_center_x - 220, hub_center_y - 140, mini_card_w, mini_card_h), 
             "MOUSE_EXT"),
            
            # Teclado - Conectado al hub, arriba centro-izquierda  
            ("SLOT_KEYBOARD", "Teclado", 
             (hub_center_x - 70, hub_center_y - 140, mini_card_w, mini_card_h), 
             "KEYBOARD_EXT"),
            
            # Monitor - Conectado al hub, arriba centro-derecha
            ("SLOT_MONITOR", "Monitor", 
             (hub_center_x + 80, hub_center_y - 140, mini_card_w, mini_card_h), 
             "MONITOR_EXT"),
            
            # Webcam - Conectado al hub, arriba derecha
            ("SLOT_WEBCAM", "Webcam", 
             (hub_center_x + 230, hub_center_y - 140, mini_card_w, mini_card_h), 
             "WEBCAM_EXT"),
            
            # Segunda fila (abajo)
            # Bocinas - Conectado al hub, abajo izquierda
            ("SLOT_HEADPHONES", "Bocinas", 
             (hub_center_x - 220, hub_center_y + 100, mini_card_w, mini_card_h), 
             "HEADPHONES_EXT"),
            
            # Micrófono - Conectado al hub, abajo centro-izquierda
            ("SLOT_PRINTER", "Micrófono", 
             (hub_center_x - 70, hub_center_y + 100, mini_card_w, mini_card_h), 
             "PRINTER_EXT"),
            
            # UPS - Conectado al hub, abajo centro-derecha
            ("SLOT_UPS", "UPS", 
             (hub_center_x + 80, hub_center_y + 100, mini_card_w, mini_card_h), 
             "UPS_EXT"),
            
            # HUB USB - Conectado al hub, abajo derecha
            ("SLOT_HUB", "HUB USB", 
             (hub_center_x + 230, hub_center_y + 100, mini_card_w, mini_card_h), 
             "HUB_EXT"),
        ]

        self.slots = []
        for id_name, display_name, coords, accepted_id in slot_data:
            slot_rect = pygame.Rect(coords[0], coords[1], coords[2], coords[3])
            self.slots.append(DropSlot(id_name, display_name, slot_rect, accepted_id))

        # Coordenadas del hub para dibujar cables
        self.hub_rect = pygame.Rect(hub_center_x - 30, hub_center_y - 15, 60, 30)

        # Componentes externos disponibles
        external_component_defs = [
            {"id": "MOUSE_EXT", "name": "Mouse Razen", "img": "../src/assets/images/componentesExternos/mouse.png", "slot": "SLOT_MOUSE"},
            {"id": "KEYBOARD_EXT", "name": "Teclado Mecanico", "img": "../src/assets/images/componentesExternos/Teclado mecánico RGB.png", "slot": "SLOT_KEYBOARD"},
            {"id": "HEADPHONES_EXT", "name": "Bocinas Estereo", "img": "../src/assets/images/componentesExternos/bocinas.png", "slot": "SLOT_HEADPHONES"},
            {"id": "WEBCAM_EXT", "name": "Webcam HD 1080p", "img": "../src/assets/images/componentesExternos/camara.png", "slot": "SLOT_WEBCAM"},
            {"id": "MONITOR_EXT", "name": "Monitor LED 24\"", "img": "../src/assets/images/componentesExternos/monitorNew.png", "slot": "SLOT_MONITOR"},
            {"id": "PRINTER_EXT", "name": "Microfono USB", "img": "../src/assets/images/componentesExternos/microfono.png", "slot": "SLOT_PRINTER"},
            {"id": "UPS_EXT", "name": "UPS", "img": "../src/assets/images/componentesExternos/ups.png", "slot": "SLOT_UPS"},
            {"id": "HUB_EXT", "name": "HUB USB", "img": "../src/assets/images/componentesExternos/HUB.png", "slot": "SLOT_HUB"},
        ]

        # Crear mini cards para componentes seleccionados distribuidas en dos columnas
        sidebar_item_y = 80
        sidebar_item_spacing = 8
        cards_per_column = 4  # 4 componentes por columna para un total de 8
        column_width = mini_card_w + 10
        
        # Centrar las columnas en el sidebar
        total_columns_width = (2 * mini_card_w) + 10
        sidebar_center_x = self.sidebar_x_start + (self.sidebar_width // 2)
        first_column_x = sidebar_center_x - (total_columns_width // 2)
        second_column_x = first_column_x + column_width
        
        self.mini_cards = []
        card_index = 0
        
        for comp_def in external_component_defs:
            if comp_def["name"] in self.selected_external_components:
                # Determinar en qué columna va este componente
                if card_index < cards_per_column:
                    # Primera columna
                    pos_x = first_column_x
                    pos_y = sidebar_item_y + (card_index * (mini_card_h + sidebar_item_spacing))
                else:
                    # Segunda columna
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

    def draw(self):
        """Dibuja la pantalla de conexión de componentes externos"""
        # Obtener posición del mouse
        mouse_pos = pygame.mouse.get_pos()
        
        # Fondo
        self.screen.fill((240, 245, 250))

        # Título
        title_font = pygame.font.Font(None, 36)
        title_text = title_font.render("Conexión de Componentes Externos", True, (30, 41, 59))
        title_rect = title_text.get_rect(center=(self.width // 2, 30))
        self.screen.blit(title_text, title_rect)

        # Dibujar ilustración de laptop
        self._draw_laptop_illustration()
        
        # Dibujar hub y cables
        self._draw_hub_and_cables()

        # Dibujar slots para componentes externos con detección de hover
        for slot in self.slots:
            is_hovering_correct = False
            if self.currently_dragged_card and \
               self.currently_dragged_card.target_slot_id == slot.id_name and \
               slot.rect.collidepoint(mouse_pos):
                is_hovering_correct = True
            self._draw_external_slot(slot, is_hovering_correct)

        # Dibujar sidebar con componentes
        self._draw_sidebar()

        # Dibujar mini cards
        for mini_card in self.mini_cards:
            mini_card.draw(self.screen)

        # Dibujar componente siendo arrastrado
        if self.currently_dragged_card:
            self.currently_dragged_card.draw(self.screen)

        # Dibujar botones
        self._draw_navigation_buttons()

        # Dibujar alerta si es necesario
        if self.show_alert:
            self._draw_alert()

    def _draw_laptop_illustration(self):
        """Dibuja la ilustración de la laptop vista desde el frente"""
        laptop_rect = self.laptop_illustration_rect
        
        # Base de la laptop (parte inferior más gruesa)
        base_height = laptop_rect.height * 0.15
        base_rect = pygame.Rect(
            laptop_rect.left + 30,
            laptop_rect.bottom - base_height,
            laptop_rect.width - 60,
            base_height
        )
        pygame.draw.rect(self.screen, (60, 70, 80), base_rect, border_radius=8)
        pygame.draw.rect(self.screen, (40, 50, 60), base_rect, 3, border_radius=8)

        # Pantalla de la laptop
        screen_rect = pygame.Rect(
            laptop_rect.left + 20,
            laptop_rect.top + 20,
            laptop_rect.width - 40,
            laptop_rect.height - base_height - 40
        )
        pygame.draw.rect(self.screen, (20, 25, 30), screen_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 110, 120), screen_rect, 2, border_radius=5)
        
        # Pantalla interior (más clara)
        inner_screen = pygame.Rect(
            screen_rect.left + 15,
            screen_rect.top + 15,
            screen_rect.width - 30,
            screen_rect.height - 30
        )
        pygame.draw.rect(self.screen, (45, 55, 65), inner_screen, border_radius=3)

        # Teclado (representado como rectángulos pequeños)
        keyboard_area = pygame.Rect(
            base_rect.left + 20,
            base_rect.top + 8,
            base_rect.width - 40,
            base_height - 16
        )
        pygame.draw.rect(self.screen, (40, 50, 60), keyboard_area, border_radius=3)
        
        # Teclas individuales (representación simplificada)
        key_size = 8
        for row in range(3):
            for col in range(10):
                key_x = keyboard_area.left + 10 + col * (key_size + 2)
                key_y = keyboard_area.top + 5 + row * (key_size + 2)
                key_rect = pygame.Rect(key_x, key_y, key_size, key_size)
                pygame.draw.rect(self.screen, (80, 90, 100), key_rect, border_radius=1)

        # Texto "LAPTOP"
        laptop_font = pygame.font.Font(None, 24)
        laptop_text = laptop_font.render("LAPTOP", True, (200, 200, 200))
        laptop_text_rect = laptop_text.get_rect(center=inner_screen.center)
        self.screen.blit(laptop_text, laptop_text_rect)

    def _draw_hub_and_cables(self):
        """Dibuja el hub USB y los cables conectados a los slots"""
        # Dibujar hub USB
        pygame.draw.rect(self.screen, (70, 80, 90), self.hub_rect, border_radius=4)
        pygame.draw.rect(self.screen, (50, 60, 70), self.hub_rect, 2, border_radius=4)
        
        # Texto del hub
        hub_font = pygame.font.Font(None, 16)
        hub_text = hub_font.render("USB HUB", True, (200, 200, 200))
        hub_text_rect = hub_text.get_rect(center=self.hub_rect.center)
        self.screen.blit(hub_text, hub_text_rect)

        # Cable principal del hub a la laptop
        laptop_connection_point = (
            self.laptop_illustration_rect.left + self.laptop_illustration_rect.width * 0.85,
            self.laptop_illustration_rect.centery
        )
        pygame.draw.line(
            self.screen, (100, 110, 120), 
            self.hub_rect.center, 
            laptop_connection_point, 
            3
        )

        # Cables del hub a cada slot
        for slot in self.slots:
            slot_center = slot.rect.center
            # Cable usando líneas simples
            pygame.draw.line(
                self.screen, (150, 160, 170), 
                self.hub_rect.center, 
                slot_center, 
                2
            )

    def _draw_external_slot(self, slot, is_hovering_correct=False):
        """Dibuja un slot para componente externo"""
        # Fondo del slot
        if slot.is_occupied():
            bg_color = (100, 200, 100)  # Verde si tiene componente
        elif is_hovering_correct:
            bg_color = (120, 255, 120)  # Verde claro si se está haciendo hover con componente correcto
        else:
            bg_color = (220, 230, 240)  # Gris claro si está vacío
        
        pygame.draw.rect(self.screen, bg_color, slot.rect, border_radius=5)
        
        # Borde más grueso y verde si hay hover correcto
        border_color = (50, 200, 50) if is_hovering_correct else (150, 160, 170)
        border_width = 3 if is_hovering_correct else 2
        pygame.draw.rect(self.screen, border_color, slot.rect, border_width, border_radius=5)
        
        # Texto del slot (si está vacío)
        if not slot.is_occupied():
            slot_font = pygame.font.Font(None, 16)
            text_color = (40, 120, 40) if is_hovering_correct else (80, 90, 100)
            slot_text = slot_font.render(slot.display_name_on_slot, True, text_color)
            slot_text_rect = slot_text.get_rect(center=slot.rect.center)
            self.screen.blit(slot_text, slot_text_rect)

    def _draw_sidebar(self):
        """Dibuja el sidebar de componentes"""
        sidebar_rect = pygame.Rect(self.sidebar_x_start, 60, self.sidebar_width, self.height - 120)
        pygame.draw.rect(self.screen, (255, 255, 255), sidebar_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 210, 220), sidebar_rect, 2, border_radius=8)
        
        # Título del sidebar
        sidebar_font = pygame.font.Font(None, 20)
        sidebar_title = sidebar_font.render("Componentes Externos", True, (50, 60, 70))
        title_rect = sidebar_title.get_rect(centerx=sidebar_rect.centerx, y=sidebar_rect.top + 10)
        self.screen.blit(sidebar_title, title_rect)

    def _draw_navigation_buttons(self):
        """Dibuja los botones de navegación"""
        button_font = pygame.font.Font(None, 24)
        
        # Botón Atrás
        pygame.draw.rect(self.screen, (220, 53, 69), self.back_button_rect, border_radius=5)
        back_text = button_font.render("Atrás", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, back_text_rect)
        
        # Botón Siguiente (era Finalizar)
        pygame.draw.rect(self.screen, (34, 197, 94), self.continue_button_rect, border_radius=5)
        continue_text = button_font.render("Siguiente", True, (255, 255, 255))
        continue_text_rect = continue_text.get_rect(center=self.continue_button_rect.center)
        self.screen.blit(continue_text, continue_text_rect)

    def _draw_alert(self):
        """Dibuja la alerta de validación"""
        # Centrar alerta
        self.alert_box_rect.center = (self.width // 2, self.height // 2)
        
        # Fondo de alerta
        pygame.draw.rect(self.screen, (254, 202, 202), self.alert_box_rect, border_radius=8)
        pygame.draw.rect(self.screen, (239, 68, 68), self.alert_box_rect, 3, border_radius=8)
        
        # Texto de alerta
        alert_font = pygame.font.Font(None, 20)
        lines = self.alert_message.split('\n')
        y_offset = self.alert_box_rect.centery - (len(lines) * 12)
        
        for line in lines:
            text_surface = alert_font.render(line, True, (153, 27, 27))
            text_rect = text_surface.get_rect(centerx=self.alert_box_rect.centerx, y=y_offset)
            self.screen.blit(text_surface, text_rect)
            y_offset += 24

    def run(self):
        """Ejecuta la lógica principal de la pantalla"""
        clock = pygame.time.Clock()
        running = True
        action_result = {"action": "quit"}

        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    action_result = {"action": "quit"}
                    running = False

                if self.show_alert:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.show_alert = False
                    continue

                # Manejo de eventos para los botones
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button_rect.collidepoint(mouse_pos):
                        action_result = {"action": "back_to_worktable", "selected_components": self.selected_external_components}
                        running = False
                        break
                    elif self.continue_button_rect.collidepoint(mouse_pos):
                        # Verificar que todos los componentes estén conectados
                        if self._all_components_connected():
                            action_result = {"action": "next_to_boot"}
                            running = False
                        else:
                            self.show_alert = True
                        break

                # Lógica de drag & drop usando el sistema existente
                if not self.show_alert:
                    if self.currently_dragged_card:
                        if self.currently_dragged_card.handle_event(event, self.slots):
                            if not self.currently_dragged_card.is_dragging:
                                self.currently_dragged_card = None

                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for card in self.mini_cards:
                            if card.rect.collidepoint(mouse_pos):
                                if card.handle_event(event, self.slots):
                                    self.currently_dragged_card = card
                                    break

            if not running:
                break

            self.draw()
            pygame.display.flip()
            clock.tick(60)

        return action_result

    def _all_components_connected(self):
        """Verifica si todos los componentes han sido conectados"""
        return all(card.is_placed for card in self.mini_cards) if self.mini_cards else True


class DesktopExternalConnectionScreen:
    """Pantalla para conectar componentes externos a la computadora de escritorio."""
    def __init__(self, screen, computer_type, selected_external_components):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.computer_type = computer_type
        self.selected_external_components = selected_external_components

        # Área para la ilustración de desktop (centro, pero un poco a la izquierda)
        self.desktop_illustration_width = self.width * 0.50
        self.desktop_illustration_height = self.height * 0.70
        self.desktop_illustration_rect = pygame.Rect(
            50, 
            (self.height - self.desktop_illustration_height) // 2 + 10, 
            self.desktop_illustration_width,
            self.desktop_illustration_height
        )

        # Área del sidebar para componentes externos (derecha)
        self.sidebar_width = self.width * 0.35
        self.sidebar_x_start = self.width - self.sidebar_width - 10

        self.slots = []
        self.mini_cards = []
        self.currently_dragged_card = None

        self._setup_desktop_external_connections()

        # Botones y Alerta
        self.show_alert = False
        self.alert_message = "Por favor conecte todos los componentes externos para continuar"
        
        button_width, button_height = 120, 35
        self.back_button_rect = pygame.Rect(20, 20, button_width, button_height)
        self.continue_button_rect = pygame.Rect(
            self.width - button_width - 20, 
            self.height - button_height - 20, 
            button_width, 
            button_height
        )
        
        self.alert_box_rect = pygame.Rect(0, 0, 400, 100)

    def _setup_desktop_external_connections(self):
        # Tarjetas para componentes externos
        mini_card_w, mini_card_h = 140, 80
        img_in_card_w, img_in_card_h = 60, 50

        # Hub USB en el lado derecho de la torre para conectar periféricos
        hub_center_x = self.desktop_illustration_rect.centerx - 50  # Cambiado de +40 a -50 para mover más a la izquierda
        hub_center_y = self.desktop_illustration_rect.centery
        
        # Slots para componentes externos distribuidos alrededor del hub
        slot_data = [
            # Primera fila (arriba)
            # Mouse - Conectado al hub, arriba izquierda
            ("SLOT_MOUSE", "Mouse", 
             (hub_center_x - 220, hub_center_y - 140, mini_card_w, mini_card_h), 
             "MOUSE_EXT"),
            
            # Teclado - Conectado al hub, arriba centro-izquierda  
            ("SLOT_KEYBOARD", "Teclado", 
             (hub_center_x - 70, hub_center_y - 140, mini_card_w, mini_card_h), 
             "KEYBOARD_EXT"),
            
            # Monitor - Conectado al hub, arriba centro-derecha
            ("SLOT_MONITOR", "Monitor", 
             (hub_center_x + 80, hub_center_y - 140, mini_card_w, mini_card_h), 
             "MONITOR_EXT"),
            
            # Webcam - Conectado al hub, arriba derecha
            ("SLOT_WEBCAM", "Webcam", 
             (hub_center_x + 230, hub_center_y - 140, mini_card_w, mini_card_h), 
             "WEBCAM_EXT"),
            
            # Segunda fila (abajo)
            # Bocinas - Conectado al hub, abajo izquierda
            ("SLOT_HEADPHONES", "Bocinas", 
             (hub_center_x - 220, hub_center_y + 100, mini_card_w, mini_card_h), 
             "HEADPHONES_EXT"),
            
            # Micrófono - Conectado al hub, abajo centro-izquierda
            ("SLOT_PRINTER", "Micrófono", 
             (hub_center_x - 70, hub_center_y + 100, mini_card_w, mini_card_h), 
             "PRINTER_EXT"),
            
            # UPS - Conectado al hub, abajo centro-derecha
            ("SLOT_UPS", "UPS", 
             (hub_center_x + 80, hub_center_y + 100, mini_card_w, mini_card_h), 
             "UPS_EXT"),
            
            # HUB USB - Conectado al hub, abajo derecha
            ("SLOT_HUB", "HUB USB", 
             (hub_center_x + 230, hub_center_y + 100, mini_card_w, mini_card_h), 
             "HUB_EXT"),
        ]

        self.slots = []
        for id_name, display_name, coords, accepted_id in slot_data:
            slot_rect = pygame.Rect(coords[0], coords[1], coords[2], coords[3])
            self.slots.append(DropSlot(id_name, display_name, slot_rect, accepted_id))

        # Coordenadas del hub para dibujar cables
        self.hub_rect = pygame.Rect(hub_center_x - 30, hub_center_y - 15, 60, 30)

        # Componentes externos disponibles (mismos que laptop)
        external_component_defs = [
            {"id": "MOUSE_EXT", "name": "Mouse Razen", "img": "../src/assets/images/componentesExternos/mouse.png", "slot": "SLOT_MOUSE"},
            {"id": "KEYBOARD_EXT", "name": "Teclado Mecanico", "img": "../src/assets/images/componentesExternos/Teclado mecánico RGB.png", "slot": "SLOT_KEYBOARD"},
            {"id": "HEADPHONES_EXT", "name": "Bocinas Estereo", "img": "../src/assets/images/componentesExternos/bocinas.png", "slot": "SLOT_HEADPHONES"},
            {"id": "WEBCAM_EXT", "name": "Webcam HD 1080p", "img": "../src/assets/images/componentesExternos/camara.png", "slot": "SLOT_WEBCAM"},
            {"id": "MONITOR_EXT", "name": "Monitor LED 24\"", "img": "../src/assets/images/componentesExternos/monitorNew.png", "slot": "SLOT_MONITOR"},
            {"id": "PRINTER_EXT", "name": "Microfono USB", "img": "../src/assets/images/componentesExternos/microfono.png", "slot": "SLOT_PRINTER"},
            {"id": "UPS_EXT", "name": "UPS", "img": "../src/assets/images/componentesExternos/ups.png", "slot": "SLOT_UPS"},
            {"id": "HUB_EXT", "name": "HUB USB", "img": "../src/assets/images/componentesExternos/HUB.png", "slot": "SLOT_HUB"},
        ]

        # Crear mini cards para componentes seleccionados distribuidas en dos columnas
        sidebar_item_y = 80
        sidebar_item_spacing = 8
        cards_per_column = 4  # 4 componentes por columna para un total de 8
        column_width = mini_card_w + 10
        
        # Centrar las columnas en el sidebar
        total_columns_width = (2 * mini_card_w) + 10
        sidebar_center_x = self.sidebar_x_start + (self.sidebar_width // 2)
        first_column_x = sidebar_center_x - (total_columns_width // 2)
        second_column_x = first_column_x + column_width
        
        self.mini_cards = []
        card_index = 0
        
        for comp_def in external_component_defs:
            if comp_def["name"] in self.selected_external_components:
                # Determinar en qué columna va este componente
                if card_index < cards_per_column:
                    # Primera columna
                    pos_x = first_column_x
                    pos_y = sidebar_item_y + (card_index * (mini_card_h + sidebar_item_spacing))
                else:
                    # Segunda columna
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

    def draw(self):
        """Dibuja la pantalla de conexión de componentes externos para desktop"""
        # Obtener posición del mouse
        mouse_pos = pygame.mouse.get_pos()
        
        # Fondo
        self.screen.fill((240, 245, 250))

        # Título
        title_font = pygame.font.Font(None, 36)
        title_text = title_font.render("Conexión de Componentes Externos - Desktop", True, (30, 41, 59))
        title_rect = title_text.get_rect(center=(self.width // 2, 30))
        self.screen.blit(title_text, title_rect)

        # Dibujar ilustración de computadora de torre
        self._draw_desktop_illustration()
        
        # Dibujar hub y cables
        self._draw_hub_and_cables()

        # Dibujar slots para componentes externos con detección de hover
        for slot in self.slots:
            is_hovering_correct = False
            if self.currently_dragged_card and \
               self.currently_dragged_card.target_slot_id == slot.id_name and \
               slot.rect.collidepoint(mouse_pos):
                is_hovering_correct = True
            self._draw_external_slot(slot, is_hovering_correct)

        # Dibujar sidebar con componentes
        self._draw_sidebar()

        # Dibujar mini cards
        for mini_card in self.mini_cards:
            mini_card.draw(self.screen)

        # Dibujar componente siendo arrastrado
        if self.currently_dragged_card:
            self.currently_dragged_card.draw(self.screen)

        # Dibujar botones
        self._draw_navigation_buttons()

        # Dibujar alerta si es necesario
        if self.show_alert:
            self._draw_alert()

    def _draw_desktop_illustration(self):
        """Dibuja la ilustración de la computadora de torre (desktop)"""
        desktop_rect = self.desktop_illustration_rect
        
        # Cuerpo principal de la torre (rectángulo vertical)
        tower_width = desktop_rect.width * 0.4
        tower_height = desktop_rect.height * 0.8
        tower_rect = pygame.Rect(
            desktop_rect.left + (desktop_rect.width - tower_width) // 2,
            desktop_rect.top + (desktop_rect.height - tower_height) // 2,
            tower_width,
            tower_height
        )
        
        # Dibujar torre principal
        pygame.draw.rect(self.screen, (70, 80, 90), tower_rect, border_radius=8)
        pygame.draw.rect(self.screen, (50, 60, 70), tower_rect, 3, border_radius=8)

        # Panel frontal (ligeramente más oscuro)
        front_panel = pygame.Rect(
            tower_rect.left + 10,
            tower_rect.top + 20,
            tower_rect.width - 20,
            tower_rect.height - 40
        )
        pygame.draw.rect(self.screen, (60, 70, 80), front_panel, border_radius=5)
        pygame.draw.rect(self.screen, (40, 50, 60), front_panel, 2, border_radius=5)

        # Botón de encendido (círculo en la parte superior)
        power_button_center = (front_panel.centerx, front_panel.top + 30)
        pygame.draw.circle(self.screen, (100, 200, 100), power_button_center, 8)
        pygame.draw.circle(self.screen, (80, 160, 80), power_button_center, 8, 2)

        # Puertos frontales (rectángulos pequeños)
        ports_y = front_panel.top + 60
        for i in range(4):
            port_rect = pygame.Rect(
                front_panel.left + 15 + (i * 25),
                ports_y,
                20, 8
            )
            pygame.draw.rect(self.screen, (30, 40, 50), port_rect, border_radius=2)

        # Ranuras de ventilación (líneas horizontales)
        vent_start_y = front_panel.top + 100
        for i in range(8):
            vent_y = vent_start_y + (i * 15)
            pygame.draw.line(
                self.screen, (40, 50, 60),
                (front_panel.left + 20, vent_y),
                (front_panel.right - 20, vent_y),
                2
            )

        # Base de la torre
        base_rect = pygame.Rect(
            tower_rect.left - 10,
            tower_rect.bottom - 15,
            tower_rect.width + 20,
            20
        )
        pygame.draw.rect(self.screen, (80, 90, 100), base_rect, border_radius=5)
        pygame.draw.rect(self.screen, (60, 70, 80), base_rect, 2, border_radius=5)

        # Texto "DESKTOP PC"
        desktop_font = pygame.font.Font(None, 20)
        desktop_text = desktop_font.render("DESKTOP PC", True, (200, 200, 200))
        desktop_text_rect = desktop_text.get_rect(center=(tower_rect.centerx, tower_rect.bottom + 40))
        self.screen.blit(desktop_text, desktop_text_rect)

        # Panel trasero con puertos (lado derecho de la torre)
        back_panel = pygame.Rect(
            tower_rect.right,
            tower_rect.top + 50,
            30,
            tower_rect.height - 100
        )
        pygame.draw.rect(self.screen, (50, 60, 70), back_panel, border_radius=3)
        pygame.draw.rect(self.screen, (30, 40, 50), back_panel, 2, border_radius=3)

        # Puertos traseros (pequeños rectángulos)
        for i in range(6):
            port_rect = pygame.Rect(
                back_panel.left + 5,
                back_panel.top + 20 + (i * 25),
                20, 12
            )
            pygame.draw.rect(self.screen, (20, 30, 40), port_rect, border_radius=2)

    def _draw_hub_and_cables(self):
        """Dibuja el hub USB y los cables conectados a los slots"""
        # Dibujar hub USB
        pygame.draw.rect(self.screen, (70, 80, 90), self.hub_rect, border_radius=4)
        pygame.draw.rect(self.screen, (50, 60, 70), self.hub_rect, 2, border_radius=4)
        
        # Texto del hub
        hub_font = pygame.font.Font(None, 16)
        hub_text = hub_font.render("USB HUB", True, (200, 200, 200))
        hub_text_rect = hub_text.get_rect(center=self.hub_rect.center)
        self.screen.blit(hub_text, hub_text_rect)

        # Cable principal del hub a la computadora de torre
        desktop_connection_point = (
            self.desktop_illustration_rect.centerx + self.desktop_illustration_rect.width * 0.35,
            self.desktop_illustration_rect.centery
        )
        pygame.draw.line(
            self.screen, (100, 110, 120), 
            self.hub_rect.center, 
            desktop_connection_point, 
            3
        )

        # Cables del hub a cada slot
        for slot in self.slots:
            slot_center = slot.rect.center
            # Cable usando líneas simples
            pygame.draw.line(
                self.screen, (150, 160, 170), 
                self.hub_rect.center, 
                slot_center, 
                2
            )

    def _draw_external_slot(self, slot, is_hovering_correct=False):
        """Dibuja un slot para componente externo"""
        # Fondo del slot
        if slot.is_occupied():
            bg_color = (100, 200, 100)  # Verde si tiene componente
        elif is_hovering_correct:
            bg_color = (120, 255, 120)  # Verde claro si se está haciendo hover con componente correcto
        else:
            bg_color = (220, 230, 240)  # Gris claro si está vacío
        
        pygame.draw.rect(self.screen, bg_color, slot.rect, border_radius=5)
        
        # Borde más grueso y verde si hay hover correcto
        border_color = (50, 200, 50) if is_hovering_correct else (150, 160, 170)
        border_width = 3 if is_hovering_correct else 2
        pygame.draw.rect(self.screen, border_color, slot.rect, border_width, border_radius=5)
        
        # Texto del slot (si está vacío)
        if not slot.is_occupied():
            slot_font = pygame.font.Font(None, 16)
            text_color = (40, 120, 40) if is_hovering_correct else (80, 90, 100)
            slot_text = slot_font.render(slot.display_name_on_slot, True, text_color)
            slot_text_rect = slot_text.get_rect(center=slot.rect.center)
            self.screen.blit(slot_text, slot_text_rect)

    def _draw_sidebar(self):
        """Dibuja el sidebar de componentes"""
        sidebar_rect = pygame.Rect(self.sidebar_x_start, 60, self.sidebar_width, self.height - 120)
        pygame.draw.rect(self.screen, (255, 255, 255), sidebar_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 210, 220), sidebar_rect, 2, border_radius=8)
        
        # Título del sidebar
        sidebar_font = pygame.font.Font(None, 20)
        sidebar_title = sidebar_font.render("Componentes Externos", True, (50, 60, 70))
        title_rect = sidebar_title.get_rect(centerx=sidebar_rect.centerx, y=sidebar_rect.top + 10)
        self.screen.blit(sidebar_title, title_rect)

    def _draw_navigation_buttons(self):
        """Dibuja los botones de navegación"""
        button_font = pygame.font.Font(None, 24)
        
        # Botón Atrás
        pygame.draw.rect(self.screen, (220, 53, 69), self.back_button_rect, border_radius=5)
        back_text = button_font.render("Atrás", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, back_text_rect)
        
        # Botón Siguiente (era Finalizar)
        pygame.draw.rect(self.screen, (34, 197, 94), self.continue_button_rect, border_radius=5)
        continue_text = button_font.render("Siguiente", True, (255, 255, 255))
        continue_text_rect = continue_text.get_rect(center=self.continue_button_rect.center)
        self.screen.blit(continue_text, continue_text_rect)

    def _draw_alert(self):
        """Dibuja la alerta de validación"""
        # Centrar alerta
        self.alert_box_rect.center = (self.width // 2, self.height // 2)
        
        # Fondo de alerta
        pygame.draw.rect(self.screen, (254, 202, 202), self.alert_box_rect, border_radius=8)
        pygame.draw.rect(self.screen, (239, 68, 68), self.alert_box_rect, 3, border_radius=8)
        
        # Texto de alerta
        alert_font = pygame.font.Font(None, 20)
        lines = self.alert_message.split('\n')
        y_offset = self.alert_box_rect.centery - (len(lines) * 12)
        
        for line in lines:
            text_surface = alert_font.render(line, True, (153, 27, 27))
            text_rect = text_surface.get_rect(centerx=self.alert_box_rect.centerx, y=y_offset)
            self.screen.blit(text_surface, text_rect)
            y_offset += 24

    def run(self):
        """Ejecuta la lógica principal de la pantalla"""
        clock = pygame.time.Clock()
        running = True
        action_result = {"action": "quit"}

        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    action_result = {"action": "quit"}
                    running = False

                if self.show_alert:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.show_alert = False
                    continue

                # Manejo de eventos para los botones
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button_rect.collidepoint(mouse_pos):
                        action_result = {"action": "back_to_worktable", "selected_components": self.selected_external_components}
                        running = False
                        break
                    elif self.continue_button_rect.collidepoint(mouse_pos):
                        # Verificar que todos los componentes estén conectados
                        if self._all_components_connected():
                            action_result = {"action": "assembly_complete"}
                            running = False
                        else:
                            self.show_alert = True
                        break

                # Lógica de drag & drop usando el sistema existente
                if not self.show_alert:
                    if self.currently_dragged_card:
                        if self.currently_dragged_card.handle_event(event, self.slots):
                            if not self.currently_dragged_card.is_dragging:
                                self.currently_dragged_card = None

                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for card in self.mini_cards:
                            if card.rect.collidepoint(mouse_pos):
                                if card.handle_event(event, self.slots):
                                    self.currently_dragged_card = card
                                    break

            if not running:
                break

            self.draw()
            pygame.display.flip()
            clock.tick(60)

        return action_result

    def _all_components_connected(self):
        """Verifica si todos los componentes han sido conectados"""
        return all(card.is_placed for card in self.mini_cards) if self.mini_cards else True 


class LaptopBootScreen:
    """Pantalla de encendido de laptop - muestra si enciende correctamente o pantalla azul"""
    def __init__(self, screen, selected_internal_components):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.selected_internal_components = selected_internal_components
        
        # Estados de la pantalla
        self.laptop_powered_on = False
        self.animation_phase = 0  # Para la animación de encendido
        self.animation_timer = 0
        self.show_message = False
        self.message_timer = 0
        
        # Verificar si todos los componentes internos están presentes
        required_laptop_components = [
            "RAM DDR4 8GB", "Ryzen 7 5700X", "Kingston SSD 1TB", 
            "M.2 NVMe SSD", "Modulo Wi-Fi/BT"
        ]
        self.all_components_present = all(comp in selected_internal_components for comp in required_laptop_components)
        
        # Área de la laptop (MUCHO MÁS ALARGADA)
        self.laptop_width = 500  # Mantener ancho
        self.laptop_height = 420  # Era 350, ahora 420 (mucho más alto)
        self.laptop_rect = pygame.Rect(
            (self.width - self.laptop_width) // 2 - 150,  # Mover más a la izquierda para dar espacio al mensaje
            (self.height - self.laptop_height) // 2 - 10,  # Centrar verticalmente
            self.laptop_width,
            self.laptop_height
        )
        
        # Área de la pantalla dentro de la laptop (ajustada proporcionalmente)
        screen_margin = 25
        self.screen_rect = pygame.Rect(
            self.laptop_rect.x + screen_margin,
            self.laptop_rect.y + screen_margin,
            self.laptop_rect.width - 2 * screen_margin,
            self.laptop_rect.height - 150  # Era 125, ahora más espacio para teclado más grande
        )
        
        # Botones
        button_width, button_height = 120, 40
        self.power_button_rect = pygame.Rect(
            self.laptop_rect.right + 50,
            self.laptop_rect.centery - button_height // 2,
            button_width,
            button_height
        )
        
        self.finish_button_rect = pygame.Rect(
            self.width - button_width - 30,
            self.height - button_height - 30,
            button_width,
            button_height
        )

    def draw(self):
        """Dibuja la pantalla de encendido de laptop"""
        # Fondo
        self.screen.fill((245, 248, 252))
        
        # Título
        title_font = pygame.font.Font(None, 36)
        title_text = title_font.render("Test de Encendido - Laptop", True, (30, 41, 59))
        title_rect = title_text.get_rect(center=(self.width // 2, 40))
        self.screen.blit(title_text, title_rect)
        
        # Dibujar laptop
        self._draw_laptop()
        
        # Dibujar botón de encendido
        self._draw_power_button()
        
        # Dibujar botón finalizar
        self._draw_finish_button()
        
        # Dibujar mensaje si está activo
        if self.show_message:
            self._draw_message()

    def _draw_laptop(self):
        """Dibuja la ilustración de la laptop idéntica a la imagen de referencia"""
        
        # === SOMBRA SUTIL ===
        shadow_offset = 6
        shadow_rect = self.laptop_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        # Sombra suave
        for i in range(4):
            alpha = 20 - (i * 5)
            shadow_color = (0, 0, 0, alpha)
            shadow_surface = pygame.Surface((shadow_rect.width + i*2, shadow_rect.height + i*2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, shadow_color, 
                           (0, 0, shadow_rect.width + i*2, shadow_rect.height + i*2), border_radius=12)
            self.screen.blit(shadow_surface, (shadow_rect.x - i, shadow_rect.y - i))
        
        # === CARCASA PRINCIPAL (COLOR GRIS PLATEADO) ===
        # Base principal gris plateado
        pygame.draw.rect(self.screen, (180, 180, 180), self.laptop_rect, border_radius=12)
        
        # Gradiente para efecto 3D sutil
        pygame.draw.rect(self.screen, (160, 160, 160), 
                        (self.laptop_rect.x + 2, self.laptop_rect.y + 2, 
                         self.laptop_rect.width - 4, self.laptop_rect.height - 4), border_radius=10)
        
        # Borde exterior oscuro
        pygame.draw.rect(self.screen, (120, 120, 120), self.laptop_rect, 3, border_radius=12)
        
        # === BISEL DE LA PANTALLA (NEGRO) ===
        bezel_margin = 15  # Bisel más grueso como en la imagen
        bezel_rect = pygame.Rect(
            self.screen_rect.x - bezel_margin,
            self.screen_rect.y - bezel_margin,
            self.screen_rect.width + 2 * bezel_margin,
            self.screen_rect.height + 2 * bezel_margin
        )
        
        # Bisel negro principal
        pygame.draw.rect(self.screen, (25, 25, 25), bezel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (15, 15, 15), bezel_rect, 2, border_radius=8)
        
        # === PANTALLA ===
        if not self.laptop_powered_on:
            # Pantalla apagada (gris claro como en la imagen)
            pygame.draw.rect(self.screen, (240, 240, 240), self.screen_rect, border_radius=4)
            # Borde sutil de la pantalla
            pygame.draw.rect(self.screen, (200, 200, 200), self.screen_rect, 1, border_radius=4)
        elif self.all_components_present:
            # Pantalla encendida exitosamente
            self._draw_successful_boot()
        else:
            # Pantalla azul de la muerte
            self._draw_blue_screen()
        
        # === CÁMARA WEB (pequeño círculo negro arriba) ===
        camera_x = self.laptop_rect.centerx
        camera_y = bezel_rect.y + 8
        pygame.draw.circle(self.screen, (10, 10, 10), (camera_x, camera_y), 3)
        pygame.draw.circle(self.screen, (40, 40, 40), (camera_x, camera_y), 2)
        
        # === ÁREA DEL TECLADO (parte inferior gris) ===
        keyboard_area_y = self.screen_rect.bottom + 25
        keyboard_area_rect = pygame.Rect(
            self.laptop_rect.x + 15,
            keyboard_area_y,
            self.laptop_rect.width - 30,
            self.laptop_rect.bottom - keyboard_area_y - 15
        )
        
        # Fondo del área del teclado (mismo gris que la carcasa)
        pygame.draw.rect(self.screen, (160, 160, 160), keyboard_area_rect, border_radius=6)
        
        # === TECLADO REALISTA ===
        # Área negra del teclado
        keyboard_rect = pygame.Rect(
            keyboard_area_rect.x + 20,
            keyboard_area_rect.y + 15,
            keyboard_area_rect.width - 40,
            65  # Altura del teclado
        )
        
        pygame.draw.rect(self.screen, (40, 40, 40), keyboard_rect, border_radius=4)
        
        # Teclas individuales realistas
        key_width = 20
        key_height = 12
        key_spacing_x = 22
        key_spacing_y = 14
        
        # Layout del teclado como en la imagen
        keyboard_rows = [
            (13, 8),   # Fila de números
            (13, 22),  # Fila QWERTY  
            (12, 36),  # Fila ASDF
            (10, 50)   # Fila ZXCV
        ]
        
        for row_idx, (keys_count, y_offset) in enumerate(keyboard_rows):
            start_x = keyboard_rect.x + (keyboard_rect.width - (keys_count * key_spacing_x)) // 2
            
            for col in range(keys_count):
                key_x = start_x + col * key_spacing_x
                key_y = keyboard_rect.y + y_offset
                
                # Tecla individual
                key_rect = (key_x, key_y, key_width, key_height)
                # Tecla gris oscuro
                pygame.draw.rect(self.screen, (70, 70, 70), key_rect, border_radius=2)
                # Borde más oscuro
                pygame.draw.rect(self.screen, (50, 50, 50), key_rect, 1, border_radius=2)
        
        # Barra espaciadora
        spacebar_width = 120
        spacebar_x = keyboard_rect.centerx - spacebar_width // 2
        spacebar_y = keyboard_rect.y + 50
        spacebar_rect = (spacebar_x, spacebar_y, spacebar_width, key_height)
        pygame.draw.rect(self.screen, (70, 70, 70), spacebar_rect, border_radius=2)
        pygame.draw.rect(self.screen, (50, 50, 50), spacebar_rect, 1, border_radius=2)
        

        
        # === BORDES Y DETALLES FINALES ===
        # Línea de separación entre pantalla y teclado
        pygame.draw.line(self.screen, (120, 120, 120), 
                        (self.laptop_rect.x + 20, keyboard_area_y), 
                        (self.laptop_rect.right - 20, keyboard_area_y), 2)
        
        # Bisagra sutil (línea en la parte superior)
        pygame.draw.line(self.screen, (100, 100, 100),
                        (self.laptop_rect.x + 30, self.laptop_rect.y + 5),
                        (self.laptop_rect.right - 30, self.laptop_rect.y + 5), 1)

    def _draw_successful_boot(self):
        """Dibuja pantalla de arranque exitoso con animación"""
        # Fondo azul claro
        base_color = (100, 150, 255)
        
        # Animación de gradiente
        if self.animation_phase < 30:  # 0.5 segundos a 60 FPS
            alpha = int((self.animation_phase / 30) * 255)
            color = (base_color[0], base_color[1], base_color[2])
        else:
            color = base_color
            
        pygame.draw.rect(self.screen, color, self.screen_rect, border_radius=5)
        
        # Logo de Windows simulado
        logo_size = 40
        logo_rect = pygame.Rect(
            self.screen_rect.centerx - logo_size // 2,
            self.screen_rect.centery - 30,
            logo_size, logo_size
        )
        
        # Dibujar logo simple (4 cuadrados)
        quad_size = logo_size // 2 - 2
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (logo_rect.x, logo_rect.y, quad_size, quad_size))
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (logo_rect.x + quad_size + 4, logo_rect.y, quad_size, quad_size))
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (logo_rect.x, logo_rect.y + quad_size + 4, quad_size, quad_size))
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (logo_rect.x + quad_size + 4, logo_rect.y + quad_size + 4, quad_size, quad_size))
        
        # Texto de carga
        font = pygame.font.Font(None, 24)
        if self.animation_phase < 60:
            text = "Iniciando..."
        else:
            text = "Windows 11"
        
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen_rect.centerx, logo_rect.bottom + 30))
        self.screen.blit(text_surface, text_rect)
        
        # Barra de progreso animada
        if self.animation_phase >= 30:
            progress_width = 150
            progress_height = 4
            progress_rect = pygame.Rect(
                self.screen_rect.centerx - progress_width // 2,
                text_rect.bottom + 20,
                progress_width, progress_height
            )
            pygame.draw.rect(self.screen, (255, 255, 255), progress_rect, border_radius=2)
            
            # Progreso
            fill_width = int((min(self.animation_phase - 30, 60) / 60) * progress_width)
            if fill_width > 0:
                fill_rect = pygame.Rect(progress_rect.x, progress_rect.y, fill_width, progress_height)
                pygame.draw.rect(self.screen, (0, 200, 100), fill_rect, border_radius=2)

    def _draw_blue_screen(self):
        """Dibuja la pantalla azul de la muerte"""
        # Fondo azul de la muerte
        pygame.draw.rect(self.screen, (0, 120, 215), self.screen_rect, border_radius=5)
        
        # Emoji triste
        font_large = pygame.font.Font(None, 72)
        sad_face = font_large.render(":(", True, (255, 255, 255))
        sad_rect = sad_face.get_rect(center=(self.screen_rect.centerx, self.screen_rect.y + 60))
        self.screen.blit(sad_face, sad_rect)
        
        # Texto de error
        font_medium = pygame.font.Font(None, 28)
        error_lines = [
            "Tu PC encontró un problema y necesita",
            "reiniciarse. Estamos recopilando información",
            "de errores y luego reiniciaremos por ti."
        ]
        
        y_start = sad_rect.bottom + 20
        for i, line in enumerate(error_lines):
            text_surface = font_medium.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.screen_rect.centerx, y_start + i * 25))
            self.screen.blit(text_surface, text_rect)
        
        # Código de error
        font_small = pygame.font.Font(None, 20)
        error_code = "CRITICAL_PROCESS_DIED"
        code_surface = font_small.render(error_code, True, (200, 200, 200))
        code_rect = code_surface.get_rect(center=(self.screen_rect.centerx, self.screen_rect.bottom - 30))
        self.screen.blit(code_surface, code_rect)

    def _draw_power_button(self):
        """Dibuja el botón de encendido"""
        # Color del botón
        if self.laptop_powered_on:
            button_color = (100, 100, 100)  # Gris cuando está encendido
        else:
            button_color = (34, 197, 94)    # Verde cuando puede presionarse
            
        pygame.draw.rect(self.screen, button_color, self.power_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, (50, 50, 50), self.power_button_rect, 2, border_radius=8)
        
        # Icono de power
        font = pygame.font.Font(None, 24)
        power_text = font.render("Encender", True, (255, 255, 255))
        power_rect = power_text.get_rect(center=self.power_button_rect.center)
        self.screen.blit(power_text, power_rect)

    def _draw_finish_button(self):
        """Dibuja el botón finalizar"""
        pygame.draw.rect(self.screen, (220, 53, 69), self.finish_button_rect, border_radius=8)
        font = pygame.font.Font(None, 24)
        finish_text = font.render("Finalizar", True, (255, 255, 255))
        finish_rect = finish_text.get_rect(center=self.finish_button_rect.center)
        self.screen.blit(finish_text, finish_rect)

    def _draw_message(self):
        """Dibuja mensaje de resultado en el lado derecho"""
        # Fondo del mensaje (MOVIDO AL LADO DERECHO)
        message_width = 320  # Era 500, más angosto
        message_height = 140  # Era 120, un poco más alto
        message_rect = pygame.Rect(
            self.laptop_rect.right + 30,  # Al lado derecho de la laptop
            self.laptop_rect.centery - message_height // 2,  # Centrado verticalmente con la laptop
            message_width, message_height
        )
        
        if self.all_components_present:
            bg_color = (200, 255, 200)  # Verde claro para éxito
            border_color = (34, 197, 94)
        else:
            bg_color = (255, 200, 200)  # Rojo claro para error
            border_color = (220, 53, 69)
            
        pygame.draw.rect(self.screen, bg_color, message_rect, border_radius=10)
        pygame.draw.rect(self.screen, border_color, message_rect, 3, border_radius=10)
        
        # Texto del mensaje (ajustado para el ancho más pequeño)
        font = pygame.font.Font(None, 22)  # Un poco más pequeño
        if self.all_components_present:
            lines = [
                "¡Excelente trabajo!",
                "",
                "Todos los componentes",
                "fueron ensamblados",
                "correctamente.",
                "",
                "La laptop enciende",
                "perfectamente."
            ]
        else:
            lines = [
                "¡Ups! La laptop no",
                "puede encender.",
                "",
                "Faltan componentes",
                "internos por ensamblar.",
                "",
                "Haz clic en Finalizar",
                "e intenta nuevamente."
            ]
        
        y_start = message_rect.y + 15
        for i, line in enumerate(lines):
            if line:  # Solo dibujar líneas no vacías
                text_surface = font.render(line, True, (50, 50, 50))
                text_rect = text_surface.get_rect(center=(message_rect.centerx, y_start + i * 16))
                self.screen.blit(text_surface, text_rect)

    def update(self, dt):
        """Actualiza animaciones"""
        if self.laptop_powered_on:
            self.animation_timer += dt
            self.animation_phase = min(int(self.animation_timer * 60), 120)  # 2 segundos máximo
        
        if self.show_message:
            self.message_timer += dt

    def run(self):
        """Ejecuta la lógica principal de la pantalla"""
        clock = pygame.time.Clock()
        running = True
        action_result = {"action": "quit"}

        while running:
            dt = clock.tick(60) / 1000.0  # Delta time en segundos
            mouse_pos = pygame.mouse.get_pos()
            
            # Actualizar animaciones
            self.update(dt)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    action_result = {"action": "quit"}
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.power_button_rect.collidepoint(mouse_pos) and not self.laptop_powered_on:
                        # Encender laptop
                        self.laptop_powered_on = True
                        self.animation_timer = 0
                        self.animation_phase = 0
                        # Mostrar mensaje después de 3 segundos
                        pygame.time.set_timer(pygame.USEREVENT + 1, 3000)
                        
                    elif self.finish_button_rect.collidepoint(mouse_pos):
                        action_result = {"action": "back_to_selection"}
                        running = False

                if event.type == pygame.USEREVENT + 1:
                    # Mostrar mensaje después de la animación
                    self.show_message = True
                    self.message_timer = 0
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancelar timer

            self.draw()
            pygame.display.flip()

        return action_result