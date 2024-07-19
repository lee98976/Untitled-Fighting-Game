import pygame


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, xDIM, yDIM):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((xDIM, yDIM))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y) 
        self.mask = pygame.mask.from_surface(self.image)
