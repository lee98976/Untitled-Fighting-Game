import pygame

class Background(pygame.sprite.Sprite):
    def __init__(self, image, scale, x, y, playerIndicator=False):  
        pygame.sprite.Sprite.__init__(self)
        width = image.get_width()  
        height = image.get_height()
        #scale image by specified scale size
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.playerIndicator=playerIndicator
    
    def updateSprite(self, x, y):
        self.rect.center = (x, y)