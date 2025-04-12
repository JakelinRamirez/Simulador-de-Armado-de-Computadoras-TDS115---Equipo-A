import pygame

class SelectionScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.title_text = self.title_font.render("Selecciona el tipo de computadora", True, (255, 255, 255))

        # Cargar y redimensionar imágenes
        self.laptop_image = pygame.image.load("../assets/images/LaptopIcon.PNG").convert_alpha()
        self.desktop_image = pygame.image.load("../assets/images/DesktopIcon.png").convert_alpha()
        self.laptop_image = pygame.transform.scale(self.laptop_image, (120, 100))
        self.desktop_image = pygame.transform.scale(self.desktop_image, (120, 100))

        # Rectángulos de tarjeta (contenedor principal)
        self.laptop_rect = pygame.Rect(150, 250, 200, 260)
        self.desktop_rect = pygame.Rect(400, 250, 200, 260)

        # Botones de seleccionar
        self.laptop_button_rect = pygame.Rect(self.laptop_rect.x + 25, self.laptop_rect.y + 190, 150, 40)
        self.desktop_button_rect = pygame.Rect(self.desktop_rect.x + 25, self.desktop_rect.y + 190, 150, 40)

    def draw(self):
        self.screen.fill((30, 30, 30))  # Fondo
        self.screen.blit(self.title_text, (100, 100))  # Título

        # Colores
        tarjeta_color = (180, 180, 180)
        boton_color = (100, 100, 200)

        # --- Tarjeta Laptop ---
        pygame.draw.rect(self.screen, tarjeta_color, self.laptop_rect, border_radius=12)
        self.screen.blit(self.laptop_image, (self.laptop_rect.x + 40, self.laptop_rect.y + 20))
        laptop_text = self.font.render("Laptop", True, (0, 0, 0))
        laptop_text_rect = laptop_text.get_rect(center=(self.laptop_rect.centerx, self.laptop_rect.y + 140))
        self.screen.blit(laptop_text, laptop_text_rect)
        pygame.draw.rect(self.screen, boton_color, self.laptop_button_rect, border_radius=8)
        laptop_btn_text = self.font.render("Seleccionar", True, (255, 255, 255))
        btn_text_rect = laptop_btn_text.get_rect(center=self.laptop_button_rect.center)
        self.screen.blit(laptop_btn_text, btn_text_rect)

        # --- Tarjeta Desktop ---
        pygame.draw.rect(self.screen, tarjeta_color, self.desktop_rect, border_radius=12)
        self.screen.blit(self.desktop_image, (self.desktop_rect.x + 40, self.desktop_rect.y + 20))
        desktop_text = self.font.render("Desktop", True, (0, 0, 0))
        desktop_text_rect = desktop_text.get_rect(center=(self.desktop_rect.centerx, self.desktop_rect.y + 140))
        self.screen.blit(desktop_text, desktop_text_rect)
        pygame.draw.rect(self.screen, boton_color, self.desktop_button_rect, border_radius=8)
        desktop_btn_text = self.font.render("Seleccionar", True, (255, 255, 255))
        btn_text_rect = desktop_btn_text.get_rect(center=self.desktop_button_rect.center)
        self.screen.blit(desktop_btn_text, btn_text_rect)

        pygame.display.flip()

    def run(self):
        running = True
        selected = None

        while running:
            self.draw()
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