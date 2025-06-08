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


class WorktableExternalComponentsScreen:
    """Pantalla de la mesa de trabajo con un esquema de Desktop/Torre dibujado."""
    def __init__(self, screen, computer_type, selected_component_names):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.computer_type = computer_type
        # Guardamos una copia para poder devolverla intacta si se presiona "Atrás"
        self.initial_selected_components = list(selected_component_names) 
        self.selected_component_names = selected_component_names
        self.desktop_image = pygame.image.load("assets/images/destock.png").convert_alpha()
        

        # Hacer la torre un poco más pequeña para dar más espacio al sidebar
        self.desktop_scheme_width = self.width * 0.40  # Reducido de 0.65 a 0.58
        self.desktop_scheme_height = self.height * 0.85
        self.desktop_scheme_rect = pygame.Rect(
            30, 
           (self.height - self.desktop_scheme_height) // 2 + 10, 
            self.desktop_scheme_width,
            self.desktop_scheme_height
        )
        self.desktop_image = pygame.transform.scale(self.desktop_image, (self.desktop_scheme_rect.width, self.desktop_scheme_rect.height))
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
        img_in_card_w, img_in_card_h = 45, 38  # Reducido de 80x60 a 60x50
        
        # Distribución reorganizada para evitar superposiciones
        padding_chasis = 35 
        slot_area_width = self.desktop_scheme_rect.width - 2 * padding_chasis
        slot_area_height = self.desktop_scheme_rect.height - 2 * padding_chasis

        # Componentes externos
        external_list = [
            {"id": "MON_1", "name": "Monitor LED 24\"", "img": "assets/images/componentesExternos/monitorNew.png" , "slot": "SLOT_MON"},
            {"id": "TEC_1", "name": "Teclado Mecanico", "img": "assets/images/componentesExternos/Teclado mecánico RGB.png", "slot": "SLOT_TEC"},
            {"id": "MOU_1", "name": "Mouse Razen", "img": "assets/images/componentesExternos/mouse.png", "slot": "SLOT_MOU"},
            {"id": "BOC_1", "name": "Bocinas Estereo", "img": "assets/images/componentesExternos/bocinas.png", "slot": "SLOT_BOC"},
            {"id": "WEB_1", "name": "Webcam HD 1080p", "img": "assets/images/componentesExternos/camara.png", "slot": "SLOT_WEB"},
            {"id": "MIC_1", "name": "Microfono USB", "img": "assets/images/componentesExternos/microfono.png", "slot": "SLOT_MIC"},
            {"id": "UPS_1", "name": "UPS", "img": "assets/images/componentesExternos/ups.png", "slot": "SLOT_UPS"},
            {"id": "HUB_1", "name": "HUB USB", "img": "assets/images/componentesExternos/HUB.png", "slot": "SLOT_HUB"},
        ]

        # Configuración para dos columnas - centradas en el sidebar
        # cards_per_column = 7  # Primera columna tendrá 7 componentes
        # column_width = mini_card_w + 8  # Ancho de cada columna con un poco más de padding
        
        # Ajustar espaciado para las tarjetas más pequeñas
        sidebar_item_y = 80  # Empezar más arriba
        sidebar_item_spacing = 6  # Menor espaciado entre tarjetas
        
        # Centrar las dos columnas en el sidebar
        # total_columns_width = (2 * mini_card_w) + 8  # Ancho total de las dos columnas
        # sidebar_center_x = self.sidebar_x_start + (self.sidebar_width // 2)
        # first_column_x = sidebar_center_x - (total_columns_width // 2)
        # second_column_x = first_column_x + column_width
        column_x = self.sidebar_x_start + (self.sidebar_width // 2) - (mini_card_w // 2)

        self.mini_cards = []
        card_index = 0

        for comp_def in external_list:
            if comp_def["name"] in self.selected_component_names:
                # Determinar en qué columna va este componente
                pos_x = column_x
                pos_y = sidebar_item_y + (card_index * (mini_card_h + sidebar_item_spacing))
                
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
        action_to_return = {"action": "quit"}
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    action_to_return = {"action": "quit"}
                    break

            self.draw(mouse_pos)  # Redibuja todo
            pygame.display.flip() 
        return action_to_return

    def draw(self, mouse_pos):
        self.screen.fill(BG_COLOR)

        # Dibujar el chasis principal del Desktop/Torre
        pygame.draw.rect(self.screen, LAPTOP_CHASSIS_COLOR, self.desktop_scheme_rect)

        img_rect = self.desktop_image.get_rect(centerx=self.desktop_scheme_rect.centerx,top=self.desktop_scheme_rect.top + 10)
        self.screen.blit(self.desktop_image, img_rect)

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
        title_surface = TITLE_FONT.render(f"Emsamble - {self.computer_type.capitalize()}", True, TITLE_TEXT_COLOR)
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