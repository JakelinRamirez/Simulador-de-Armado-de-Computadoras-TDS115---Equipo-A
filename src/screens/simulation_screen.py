import pygame

class EstanteScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.button_font = pygame.font.Font(None, 36)

        # Texto de los estantes
        self.internal_text = self.font.render("Componentes Internos", True, (255, 255, 255))
        self.external_text = self.font.render("Componentes Externos", True, (255, 255, 255))

        # Crear las rectas para los componentes internos (5, 5, 2)
        self.internal_components = [pygame.Rect(100 + (i % 5) * 120, 100 + (i // 5) * 100, 100, 40) for i in range(12)]  # 12 componentes internos

        # Crear las rectas para los componentes externos (4, 4)
        self.external_components = [pygame.Rect(50 + (i % 4) * 180, 100 + (i // 4) * 100, 150, 40) for i in range(8)]  # 8 componentes externos

        # Botón de cambiar entre estantes
        self.switch_button_text = self.button_font.render("Cambiar Estante", True, (255, 255, 255))
        self.switch_button_rect = self.switch_button_text.get_rect(center=(400, 550))  # Posición del botón

        self.show_internal = True  # Inicialmente mostrar los componentes internos

    def draw(self):
        self.screen.fill((30, 30, 30))  # Fondo oscuro

        # Título del estante
        if self.show_internal:
            self.screen.blit(self.internal_text, (200, 50))  # Título de componentes internos
            for i, rect in enumerate(self.internal_components):
                pygame.draw.rect(self.screen, (100, 100, 255), rect)  # Dibujar componentes internos
        else:
            self.screen.blit(self.external_text, (200, 50))  # Título de componentes externos
            for i, rect in enumerate(self.external_components):
                pygame.draw.rect(self.screen, (200, 100, 100), rect)  # Dibujar componentes externos

        # Dibujar el botón para cambiar de estante
        pygame.draw.rect(self.screen, (70, 130, 180), self.switch_button_rect.inflate(20, 20))  # Botón con borde
        self.screen.blit(self.switch_button_text, self.switch_button_rect)  # Botón con texto

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.switch_button_rect.collidepoint(event.pos):
                        self.show_internal = not self.show_internal  # Cambiar entre estantes

        pygame.quit()