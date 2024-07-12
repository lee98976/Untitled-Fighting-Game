from backgrounds.background import background
import pygame

class ImgPlatform(background):
    """Inherits background, but contains mask for object detection"""
    def __init__(self, image, scale, x, y):
        super().__init__(image, scale, x, y)
        self.mask = pygame.mask.from_surface(self.image)