import pygame

class BlockBar(pygame.sprite.Sprite):
    def __init__(self, owner, x, y, flipped=False): #Current health starts at maxHealth
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("sprites/blockBar/block1.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 3, self.image.get_height() * 3))
        self.image = pygame.transform.flip(self.image, flipped, False)
        self.rect = self.image.get_rect()
        self.owner = owner
        self.flipped = flipped
        self.rect.topleft = (x, y)

    def updateSprite(self, maxBlockHealth, blockHealth, posX, posY):
        if blockHealth > 0:
            number =  int(maxBlockHealth - blockHealth) // int(maxBlockHealth/10) + 1
            if number < 1:
                number = 1
            elif number > 10:
                number = 10
            self.image = pygame.image.load("sprites/blockBar/block" + str(number) + ".png") 
        else:
            self.image = pygame.load("sprites/blockBar/blockBreak.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 3, self.image.get_height() * 3))
        self.image = pygame.transform.flip(self.image, self.flipped, False)
        self.rect = self.image.get_rect()
        self.rect.topleft = (posX, posY)