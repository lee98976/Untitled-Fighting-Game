from os import name
import pygame


class Hitbox(pygame.sprite.Sprite):
    def __init__(self, name, xPos, yPos, velocityX, velocityY, activeFrames, damage, knockback, stunFrames, invisFrames, owner, attackID):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.image = pygame.image.load("game/sprites/swordFighter/attackSprites/" + name + ".png")
        self.image = pygame.transform.scale(self.image, (3 * self.image.get_width(), 3 * self.image.get_height()))
        if velocityX < 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.center = (xPos, yPos)
        self.mask = pygame.mask.from_surface(self.image)
        self.activeFrames = activeFrames
        self.currentFrames = 0
        self.damage = damage
        self.knockback = knockback
        self.stunFrames = stunFrames
        self.invisFrames = invisFrames
        self.hitPlayers = list()
        self.x = xPos
        self.y = yPos
        self.velocityX = velocityX
        self.velocityY = velocityY
        self.owner = owner
        self.attackID = attackID

    def updateSprite(self):
        self.currentFrames += 1
        self.x += self.velocityX
        self.y += self.velocityY
        self.rect.center = (self.x, self.y)
        if self.currentFrames > self.activeFrames:
            self.kill()