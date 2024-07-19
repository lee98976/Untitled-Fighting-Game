import pygame

class ImgPlatform(pygame.sprite.Sprite):
    """Inherits background, but contains mask for object detection"""
    def __init__(self, image, scaleX, scaleY, x, y):
        pygame.sprite.Sprite.__init__(self)
        width = image.get_width()  
        height = image.get_height()
        #scale image by specified scale size
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(image, (int(width * scaleX), int(height * scaleY)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)