import pygame

class StartScreen:
    #Constructor
    def __init__(self, screen):
        # Guarda la pantalla de Pygame y define dos tamaños de fuente: una grande para títulos y otra más pequeña para textos secundarios.
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)

        # Cargando el logo y su tamaño
        self.logo = pygame.image.load("../assets/images/logo.png").convert_alpha()
        self.logo = pygame.transform.smoothscale(self.logo, (200, 200))  

        # Configurando boton
        self.button_rect = pygame.Rect(250, 400, 300, 60)  # x, y, ancho, alto
        self.button_color = (70, 130, 180)  # Azul acero
        self.button_text = self.small_font.render("Iniciar Simulación", True, (255, 255, 255))
    
    #Metodo que dibuja en pantalla los componentes
    def draw(self):
        self.screen.fill((30, 30, 30))

        # Mostrando el logo centrado
        logo_x = (self.screen.get_width() - self.logo.get_width()) // 2
        self.screen.blit(self.logo, (logo_x, 80))

        # Dibujando botón
        pygame.draw.rect(self.screen, self.button_color, self.button_rect, border_radius=10)
        text_rect = self.button_text.get_rect(center=self.button_rect.center)
        self.screen.blit(self.button_text, text_rect)

        pygame.display.flip()

    def run(self):
        # Variables de control
        running = True
        start_simulation = False

        #While para saber que acciones que realiza el usuario
        while running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_rect.collidepoint(event.pos):
                        start_simulation = True
                        running = False
        return start_simulation