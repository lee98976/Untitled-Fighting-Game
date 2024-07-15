import pygame

class ImgPlatform(pygame.sprite.Sprite):
    """Inherits background, but contains mask for object detection"""
    def __init__(self, image, scale, x, y):
        pygame.sprite.Sprite.__init__(self)
        width = image.get_width()  
        height = image.get_height()
        #scale image by specified scale size
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.mask = pygame.mask.from_surface(self.image)