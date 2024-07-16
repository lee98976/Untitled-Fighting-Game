from os import name
import pygame


class Particle(pygame.sprite.Sprite):
    def __init__(self, image, xPos, yPos, velocityX, velocityY, activeFrames):
        pygame.sprite.Sprite.__init__(self)

        # Image process
        self.image = image
        self.image = pygame.transform.scale(self.image, (3 * self.image.get_width(), 3 * self.image.get_height()))
        if velocityX < 0:
            self.image = pygame.transform.flip(self.image, True, False)
        
        self.rect = self.image.get_rect()
        self.rect.center = (xPos, yPos)
        self.mask = pygame.mask.from_surface(self.image)
        self.activeFrames = activeFrames

        self.currentFrames = 0
        self.x = xPos
        self.y = yPos
        self.velocityX = velocityX
        self.velocityY = velocityY

    def updateSprite(self):
        self.currentFrames += 1
        self.x += self.velocityX
        self.y += self.velocityY
        self.rect.center = (self.x, self.y)
        if self.currentFrames > self.activeFrames:
            self.kill()