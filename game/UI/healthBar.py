import pygame

class HealthBar(pygame.sprite.Sprite):
    def __init__(self, owner, x, y, flipped=False): #Current health starts at maxHealth
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("sprites/healthBar/HealthBar1.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 5, self.image.get_height() * 5))
        self.image = pygame.transform.flip(self.image, flipped, False)
        self.rect = self.image.get_rect()
        self.owner = owner
        self.flipped = flipped
        self.rect.topleft = (x, y)

    def updateSprite(self, maxHealth, health):
        number =  int(maxHealth - health) // int(maxHealth/15) + 1
        if number < 1:
            number = 1
        elif number > 15:
            number = 15
        self.image = pygame.image.load("sprites/healthBar/HealthBar" + str(number) + ".png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 5, self.image.get_height() * 5))
        self.image = pygame.transform.flip(self.image, self.flipped, False)