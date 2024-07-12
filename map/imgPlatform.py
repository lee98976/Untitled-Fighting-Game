from backgrounds.background import Background
import pygame

class ImgPlatform(Background):
    """Inherits background, but contains mask for object detection"""
    def __init__(self, image, scale, x, y):
        super().__init__(image, scale, x, y)
        self.mask = pygame.mask.from_surface(self.image)