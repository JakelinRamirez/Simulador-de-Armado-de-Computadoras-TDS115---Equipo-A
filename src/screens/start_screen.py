import pygame

class StartScreen:
    """Pantalla de bienvenida del simulador de computadoras"""
    
    def __init__(self, screen):
        # Configuración básica de pantalla y fuentes
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Paleta de colores moderna - Tonos azules tecnológicos
        self.bg_color = (15, 23, 42)        # Azul marino oscuro
        self.accent_color = (59, 130, 246)   # Azul vibrante
        self.secondary_color = (147, 197, 253) # Azul claro
        self.text_color = (248, 250, 252)    # Blanco hueso
        self.button_color = (37, 99, 235)    # Azul botón
        self.button_hover = (29, 78, 216)    # Azul hover
        
        # Fuentes con tamaños específicos
        self.title_font = pygame.font.Font(None, 64)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.button_font = pygame.font.Font(None, 28)
        
        # Cargar y redimensionar logo
        self.logo = pygame.image.load("assets/images/logo.png").convert_alpha()
        self.logo = pygame.transform.smoothscale(self.logo, (180, 180))
        
        # Textos principales
        self.title_text = self.title_font.render("Simulador de Computadoras", True, self.text_color)
        self.subtitle_text = self.subtitle_font.render("Aprende armando paso a paso", True, self.secondary_color)
        
        # Configuración del botón principal
        self.button_rect = pygame.Rect(0, 0, 320, 65)
        self.button_rect.centerx = self.width // 2
        self.button_rect.y = 480
        self.button_text = self.button_font.render("Iniciar Simulacion", True, self.text_color)
        
        # Estado del botón para hover
        self.button_hovered = False
    
    def draw_gradient_rect(self, rect, color1, color2):
        """Dibuja un rectángulo con gradiente vertical"""
        for y in range(rect.height):
            # Interpolar entre los dos colores
            ratio = y / rect.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            
            pygame.draw.line(self.screen, (r, g, b), 
                           (rect.x, rect.y + y), 
                           (rect.x + rect.width, rect.y + y))
    
    def draw_shadow(self, rect, offset=5):
        """Dibuja una sombra suave para el botón"""
        shadow_rect = rect.copy()
        shadow_rect.x += offset
        shadow_rect.y += offset
        pygame.draw.rect(self.screen, (0, 0, 0, 50), shadow_rect, border_radius=15)
    
    def draw(self):
        """Renderiza todos los elementos de la pantalla"""
        # Fondo con gradiente sutil
        self.draw_gradient_rect(pygame.Rect(0, 0, self.width, self.height), 
                               self.bg_color, (25, 33, 52))
        
        # Logo centrado
        logo_x = (self.width - self.logo.get_width()) // 2
        self.screen.blit(self.logo, (logo_x, 100))
        
        # Título principal centrado
        title_rect = self.title_text.get_rect(center=(self.width // 2, 320))
        self.screen.blit(self.title_text, title_rect)
        
        # Subtítulo centrado
        subtitle_rect = self.subtitle_text.get_rect(center=(self.width // 2, 365))
        self.screen.blit(self.subtitle_text, subtitle_rect)
        
        # Sombra del botón
        self.draw_shadow(self.button_rect)
        
        # Botón con efecto hover
        button_color = self.button_hover if self.button_hovered else self.button_color
        pygame.draw.rect(self.screen, button_color, self.button_rect, border_radius=15)
        
        # Borde del botón
        pygame.draw.rect(self.screen, self.secondary_color, self.button_rect, 2, border_radius=15)
        
        # Texto del botón centrado
        text_rect = self.button_text.get_rect(center=self.button_rect.center)
        self.screen.blit(self.button_text, text_rect)
        
        pygame.display.flip()

    def run(self):
        """Maneja los eventos y la lógica principal de la pantalla"""
        running = True
        start_simulation = False
        
        while running:
            # Detectar hover del botón
            mouse_pos = pygame.mouse.get_pos()
            self.button_hovered = self.button_rect.collidepoint(mouse_pos)
            
            self.draw()
            
            # Procesar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_rect.collidepoint(event.pos):
                        start_simulation = True
                        running = False
                        
        return start_simulation