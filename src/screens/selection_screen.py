import pygame

class SelectionScreen:
    """Pantalla para seleccionar tipo de computadora (Laptop o Desktop)"""
    
    def __init__(self, screen):
        # Configuración básica de pantalla
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Paleta de colores coherente con el diseño principal
        self.bg_color = (15, 23, 42)        # Azul marino oscuro
        self.card_color = (30, 41, 59)      # Gris azulado para tarjetas
        self.card_hover = (51, 65, 85)      # Color hover para tarjetas
        self.accent_color = (59, 130, 246)   # Azul vibrante
        self.text_color = (248, 250, 252)    # Blanco hueso
        self.button_color = (37, 99, 235)    # Azul botón
        self.button_hover = (29, 78, 216)    # Azul hover
        
        # Fuentes mejoradas
        self.title_font = pygame.font.Font(None, 52)
        self.card_font = pygame.font.Font(None, 32)
        self.button_font = pygame.font.Font(None, 24)
        
        # Texto del título
        self.title_text = self.title_font.render("Selecciona el tipo de computadora", True, self.text_color)
        
        # Cargar y redimensionar imágenes
        self.laptop_image = pygame.image.load("assets/images/LaptopIcon.png").convert_alpha()
        self.desktop_image = pygame.image.load("assets/images/DesktopIcon.png").convert_alpha()
        self.laptop_image = pygame.transform.scale(self.laptop_image, (140, 120))
        self.desktop_image = pygame.transform.scale(self.desktop_image, (140, 120))
        
        # Configuración de tarjetas más grandes y centradas
        card_width, card_height = 280, 320
        spacing = 60
        total_width = 2 * card_width + spacing
        start_x = (self.width - total_width) // 2
        
        self.laptop_rect = pygame.Rect(start_x, 200, card_width, card_height)
        self.desktop_rect = pygame.Rect(start_x + card_width + spacing, 200, card_width, card_height)
        
        # Botones dentro de las tarjetas
        button_width, button_height = 200, 50
        self.laptop_button_rect = pygame.Rect(
            self.laptop_rect.x + (card_width - button_width) // 2,
            self.laptop_rect.y + card_height - 70,
            button_width, button_height
        )
        self.desktop_button_rect = pygame.Rect(
            self.desktop_rect.x + (card_width - button_width) // 2,
            self.desktop_rect.y + card_height - 70,
            button_width, button_height
        )
        
        # Estados de hover
        self.laptop_hovered = False
        self.desktop_hovered = False
        self.laptop_btn_hovered = False
        self.desktop_btn_hovered = False
    
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
    
    def draw_card_shadow(self, rect, offset=8):
        """Dibuja sombra para las tarjetas"""
        shadow_rect = rect.copy()
        shadow_rect.x += offset
        shadow_rect.y += offset
        pygame.draw.rect(self.screen, (0, 0, 0, 30), shadow_rect, border_radius=20)
    
    def draw_card(self, rect, image, title, button_rect, is_hovered, btn_hovered):
        """Dibuja una tarjeta completa con imagen, título y botón"""
        # Sombra de la tarjeta
        self.draw_card_shadow(rect)
        
        # Color de la tarjeta según hover
        card_color = self.card_hover if is_hovered else self.card_color
        pygame.draw.rect(self.screen, card_color, rect, border_radius=20)
        
        # Borde de la tarjeta
        border_color = self.accent_color if is_hovered else (71, 85, 105)
        pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=20)
        
        # Imagen centrada en la parte superior
        img_x = rect.x + (rect.width - image.get_width()) // 2
        img_y = rect.y + 30
        self.screen.blit(image, (img_x, img_y))
        
        # Título centrado
        title_text = self.card_font.render(title, True, self.text_color)
        title_rect = title_text.get_rect(center=(rect.centerx, rect.y + 180))
        self.screen.blit(title_text, title_rect)
        
        # Botón con hover
        btn_color = self.button_hover if btn_hovered else self.button_color
        pygame.draw.rect(self.screen, btn_color, button_rect, border_radius=12)
        
        # Texto del botón
        btn_text = self.button_font.render("Seleccionar", True, self.text_color)
        btn_text_rect = btn_text.get_rect(center=button_rect.center)
        self.screen.blit(btn_text, btn_text_rect)
    
    def draw(self):
        """Renderiza todos los elementos de la pantalla"""
        # Fondo con gradiente
        self.draw_gradient_rect(pygame.Rect(0, 0, self.width, self.height), 
                               self.bg_color, (25, 33, 52))
        
        # Título centrado
        title_rect = self.title_text.get_rect(center=(self.width // 2, 120))
        self.screen.blit(self.title_text, title_rect)
        
        # Dibujar tarjetas
        self.draw_card(self.laptop_rect, self.laptop_image, "Laptop", 
                      self.laptop_button_rect, self.laptop_hovered, self.laptop_btn_hovered)
        
        self.draw_card(self.desktop_rect, self.desktop_image, "Desktop", 
                      self.desktop_button_rect, self.desktop_hovered, self.desktop_btn_hovered)
        
        pygame.display.flip()

    def run(self):
        """Maneja eventos y lógica principal de selección"""
        running = True
        selected = None
        
        while running:
            # Detectar hover en tarjetas y botones
            mouse_pos = pygame.mouse.get_pos()
            self.laptop_hovered = self.laptop_rect.collidepoint(mouse_pos)
            self.desktop_hovered = self.desktop_rect.collidepoint(mouse_pos)
            self.laptop_btn_hovered = self.laptop_button_rect.collidepoint(mouse_pos)
            self.desktop_btn_hovered = self.desktop_button_rect.collidepoint(mouse_pos)
            
            self.draw()
            
            # Procesar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.laptop_button_rect.collidepoint(event.pos):
                        selected = "laptop"
                        running = False
                    elif self.desktop_button_rect.collidepoint(event.pos):
                        selected = "desktop"
                        running = False
                        
        return selected