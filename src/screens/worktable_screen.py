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

pygame.font.init() # Asegurar que las fuentes estén inicializadas
TITLE_FONT = pygame.font.Font(None, 30)
SIDEBAR_FONT = pygame.font.Font(None, 26)
MINI_CARD_FONT = pygame.font.Font(None, 18) # Un poco más grande para el nombre en la tarjeta
SLOT_NAME_FONT = pygame.font.Font(None, 20) # Para el nombre del slot (RAM, CPU)

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
        self.selected_component_names = selected_component_names

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

    def _setup_laptop_scheme_and_components(self):
        # El tamaño de los slots DEBE ser igual al de las MiniCardComponent
        mini_card_w, mini_card_h = 170, 95 # Tamaño actual de mini-tarjeta
        img_in_card_w, img_in_card_h = 80, 60 # Tamaño de imagen dentro de la mini-tarjeta

        # Coordenadas (x, y, w, h) relativas al self.laptop_scheme_rect.topleft
        # Basadas en la distribución de la imagen de referencia:
        # RAM (izquierda, un poco abajo del centro vertical del área de slots)
        # CPU (centro, arriba)
        # M.2 (derecha de CPU, arriba)
        # SSD (debajo de M.2 y parte de CPU)
        # Wi-Fi (debajo de SSD, más pequeño)
        
        # Calcular un área útil dentro del chasis para colocar los slots
        # Dejamos un padding interno en el chasis
        padding_chasis = 30 
        slot_area_x = self.laptop_scheme_rect.left + padding_chasis
        slot_area_y = self.laptop_scheme_rect.top + self.laptop_scheme_rect.height * 0.15 # Debajo del área de "pantalla"
        slot_area_width = self.laptop_scheme_rect.width - 2 * padding_chasis
        slot_area_height = self.laptop_scheme_rect.height * 0.8 - padding_chasis

        # Ajuste de coordenadas relativas al chasis (self.laptop_scheme_rect.topleft)
        slot_data = [
            # (id_slot, texto_visible_en_slot, (rel_x, rel_y, width, height), id_componente_aceptado)
            # Las dimensiones (width, height) aquí deben ser las de mini_card_w, mini_card_h
            ("SLOT_RAM", "RAM", 
             (padding_chasis + 20, slot_area_height * 0.4, mini_card_w, mini_card_h), 
             "RAM_1"),
            
            ("SLOT_CPU", "CPU", 
             (slot_area_width * 0.5 - mini_card_w * 0.5, padding_chasis + 60, mini_card_w, mini_card_h), 
             "CPU_1"),
            
            ("SLOT_M2", "M.2", 
             (slot_area_width * 0.75 - mini_card_w * 0.5, padding_chasis + 50, mini_card_w, mini_card_h), 
             "M2_1"),
            
            ("SLOT_SSD", "SSD", 
             (slot_area_width * 0.6 - mini_card_w * 0.5, slot_area_height * 0.55, mini_card_w, mini_card_h), 
             "SSD_1"),
            
            ("SLOT_WIFI", "Wi-Fi", 
             (slot_area_width * 0.55 - mini_card_w * 0.5, slot_area_height * 0.8 - mini_card_h*0.5 , mini_card_w, mini_card_h), 
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
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return {"action": "quit"}
                
                # Primero, manejar el componente que se está arrastrando, si existe
                if self.currently_dragged_card:
                    if self.currently_dragged_card.handle_event(event, self.slots):
                        # Si el evento fue MOUSEBUTTONUP y la tarjeta no se colocó, ya regresó a sidebar.
                        # Si se colocó, su estado is_placed es True.
                        if not self.currently_dragged_card.is_dragging: # Se soltó
                            self.currently_dragged_card = None
                        continue # Evento manejado por la tarjeta arrastrada
                
                # Si no se está arrastrando nada, o el evento no fue para la tarjeta arrastrada,
                # verificar si se inicia un nuevo arrastre.
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for card in self.mini_cards: # Iterar sobre todas las tarjetas
                        if card.rect.collidepoint(mouse_pos):
                            # No se puede arrastrar si el slot destino ya está ocupado por OTRA tarjeta
                            can_drag_this = True
                            if not card.is_placed: # Solo chequear si está en sidebar y queremos moverla a un slot
                                for slot_check in self.slots:
                                    if slot_check.id_name == card.target_slot_id and slot_check.is_occupied():
                                        can_drag_this = False
                                        print(f"Slot {slot_check.display_name_on_slot} ya está ocupado.")
                                        break
                            
                            if can_drag_this:
                                if card.handle_event(event, self.slots): # Inicia el arrastre
                                    self.currently_dragged_card = card
                                    break # Solo una tarjeta se arrastra a la vez
            
            self.draw(mouse_pos)
            pygame.display.flip()
            clock.tick(60)
        return {"action": "back_to_selection"}

    def draw(self, mouse_pos):
        self.screen.fill(BG_COLOR)
        
        pygame.draw.rect(self.screen, LAPTOP_CHASSIS_COLOR, self.laptop_scheme_rect, border_radius=15)
        pygame.draw.rect(self.screen, (100,100,100), self.laptop_scheme_rect, 3, border_radius=15)
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
        pygame.draw.rect(self.screen, TITLE_BG_COLOR, title_bg_rect, border_radius=6)
        title_rect = title_surface.get_rect(center=title_bg_rect.center)
        self.screen.blit(title_surface, title_rect) 