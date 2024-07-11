import json
import os
import random

import pygame

from fightingTypes.hitbox import Hitbox


class SwordFighter(pygame.sprite.Sprite):
    def __init__(self, screen, attackGroup, x, y, owned, name):
        pygame.sprite.Sprite.__init__(self)

        # How to add a attack:
        # 1. Edit anim paths
        # 2. Edit attack functions
        # 3. Edit update frame impact frame
        # 4. Create json file for attack
        self.owned = owned
        self.name = name

        #Game mechanics
        self.health = 100
        self.maxHealth = 100
        self.maxBlockHealth = 20
        self.blockHealth = 20
        self.weight = 100
        self.stunFrames = 0
        self.invisFrames = 0
        self.parryFrames = 0

        # Animation
        self.currentFrame = 0
        self.images, self.attackImages, self.frameData = self.imageProcess()
        self.lastState = "idle"
        self.state = "idle"
        self.lastKeyState = pygame.key.get_pressed()
        self.lastMouseState = pygame.key.get_pressed()
        self.facingRight = True
        self.screen = screen
        self.currentImage = 0
        self.image = self.images[self.state][0]

        # Movement
        self.x = x
        self.y = y
        self.velocity = [0.0, 0.0]
        self.onPlatform = False
        self.doubleJump = True #TODO

        # Attacking
        self.attackGroup = attackGroup
        # self.startUp = 0
        # self.currentAttack = ""
        # self.endLag = 0
        
        # Update
        self.updateSprite()


    def imageProcess(self):
        imagesPath = "sprites/swordFighter/"
        animPaths = ["idle", "walk", "drawSword", "block"]
        with open("sprites/swordFighter/frameData.json", "r") as stuff:
            frameData = json.loads(stuff.read())
        
        images = {}
        attackImages = {}
        
        for path in animPaths:
            images[path] = [
                pygame.transform.scale(
                    pygame.image.load(imagesPath + path + "/" + image),
                    (
                        int(pygame.image.load(imagesPath + path + "/" + image).get_width() * 3),
                        int(pygame.image.load(imagesPath + path + "/" + image).get_height() * 3)
                    )
                )
                for image in os.listdir(imagesPath + path)
            ]

        for image in os.listdir(imagesPath + "attackSprites"):
            attackImages[image]= pygame.transform.scale(
                        pygame.image.load(imagesPath + "attackSprites" + "/" + image),
                        (
                            int(pygame.image.load(imagesPath + "attackSprites" + "/" + image).get_width() * 3),
                            int(pygame.image.load(imagesPath + "attackSprites" + "/" + image).get_height() * 3)
                        )
            )
            
        # print("All sprites:", images)
        return images, attackImages, frameData

    def movement(self):
        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_w] and keystate[pygame.K_w] != self.lastKeyState[pygame.K_w]: # jump TODO: detect if on ground before jump
            # print(self.onPlatform, self.doubleJump)
            if self.onPlatform:   
                self.velocity[1] = 3
                print("jump")
            elif self.doubleJump:
                self.doubleJump = False
                self.velocity[1] = 5
        if keystate[pygame.K_s]: # phase through platforms
            pass
        if keystate[pygame.K_a]: 
            self.velocity[0] -= 0.2
            self.velocity[0] = max(self.velocity[0], -2)
            self.facingRight = False
            self.state = "walk"
        if keystate[pygame.K_d]:
            self.velocity[0] += 0.2
            self.velocity[0] = min(self.velocity[0], 2)
            self.facingRight = True
            self.state = "walk"
        
        
        if not(keystate[pygame.K_w] or keystate[pygame.K_a] or keystate[pygame.K_s] or keystate[pygame.K_d]): # idle animation
            self.state = "idle"

        self.lastKeyState = keystate

    def checkBlock(self):
        keystate = pygame.key.get_pressed()

        if self.blockHealth > 0:
            if keystate[pygame.K_SPACE]: # block/parry
                if keystate[pygame.K_SPACE] != self.lastKeyState[pygame.K_SPACE]:
                    self.parryFrames = 20
                self.state = "block"
            else:
                if self.state == "block":
                    self.state = "idle"

        self.lastKeyState = keystate

    def attack(self):
        mouseState = pygame.mouse.get_pressed()
    
        if mouseState[0] and self.lastMouseState[0] != mouseState[0]: # Sword slash
            self.state = "drawSword"
            self.currentFrame = 0
            self.currentImage = 0
            self.velocity = [0.0, 0.0]
            return True

        self.lastMouseState = mouseState

    def checkHealth(self):
        if self.health <= 0:
            print("Player has died!")
        elif self.health > self.maxHealth:
            self.health = self.maxHealth
        if self.blockHealth > self.maxBlockHealth:
            self.blockHealth = self.maxBlockHealth

    def calcVelocity(self):
        keystate = pygame.key.get_pressed()
        if self.velocity[0] > 2 or self.velocity[0] < -2:
            self.velocity[0] = self.velocity[0] * 0.9
        if self.velocity[1] > 3:
            self.velocity[1] = self.velocity[1] * 0.9
        if not self.onPlatform:
            self.velocity[1] -= 0.1

        if not(keystate[pygame.K_a] or keystate[pygame.K_d]) or self.state == "block":
            if self.velocity[0] > 0.1:
                self.velocity[0] -= 0.1
            elif self.velocity[0] < -0.1:
                self.velocity[0] += 0.1
            else:
                self.velocity[0] = 0

    def updateFrame(self):
        # print(self.frameData[self.state]["loop"])

        # print(self.state + str(self.currentImage + 1))
        #Conditions for looping:
        #1. State is not last state OR
        #2. Frame has run to completetion
        if self.lastState != self.state or self.currentFrame >= self.frameData[self.state][self.state + str(len(self.frameData[self.state]) - 1)][-1]:
            self.currentFrame = 0
            self.currentImage = 0
            if self.currentFrame >= self.frameData[self.state][self.state + str(len(self.frameData[self.state]) - 1)][-1] and not self.frameData[self.state]["loop"]:
                self.state = "idle"
        else:
            if self.currentFrame >= self.frameData[self.state][self.state + str(int(self.currentImage+1))][-1]:
                self.currentImage += 1
                
    
                if self.state in ["drawSword"] and self.frameData[self.state][self.state + str(self.currentImage + 1)][0] == 1:
                    #Summon Attack
                    # print("Bro attacked off")
                    if self.state == "drawSword":
                        if self.facingRight:
                            offsetX = 60
                            velocityX = 5
                            direction = 1
                        else:
                            offsetX = 10
                            velocityX = -5
                            direction = -1
    
                        summonedAttack = Hitbox("drawSword", self.x + offsetX, self.y + 50, velocityX, 0, 100, 5, [4 * direction, 2], 30, 20, self.name, random.randint(1, 184467440737095516))
                        self.attackGroup.add(summonedAttack)
    
            

        self.x += self.velocity[0]
        self.y -= self.velocity[1]


        if self.facingRight:
            self.image = self.images[self.state][self.currentImage]
        else:
            self.image = self.images[self.state][self.currentImage]
            self.image = pygame.transform.flip(self.image, True, False)

        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.mask.get_rect(topleft = (int(self.x), int(self.y)))

    def hit(self, damage, knockback, stunFrames, invisFrames):
        if self.invisFrames <= 0:
            if self.state != "block":
                self.health -= damage
                # Formula for knockback is base knockback * self.weight / 100 * (maxHealth - health)
                knockbackX = knockback[0] * self.weight / 100 * (self.maxHealth-self.health) / 20
                knockbackY = knockback[1] * self.weight / 100 * (self.maxHealth-self.health) / 20
                self.velocity = [knockbackX, knockbackY]
                self.stunFrames = stunFrames
                self.invisFrames = invisFrames
                self.state = "idle" # TODO: add hit animation
            else:
                if self.parryFrames > 0:
                    print("Opponent parried!")
                    self.stunFrames = 0
                    self.invisFrames = 10
                    self.blockHealth += 1
                else:
                    print("Opponent blocked.")
                    self.health -= int(damage / 4)
                    self.blockHealth -= damage * 3 / 4

                    if self.blockHealth < 0:
                        print("Opponent's block broke!")
                        self.stunFrames = 90
                        self.invisFrames = 0
                        self.blockHealth = -5
                        self.state = "idle" 
        else:
            print("Player is still invicible.")
    
    def updateSprite(self):
        """
        Update determines the current animation. When no input has been recieved within a certain 
        time frame and is grounded, it will go back to idle. Otherwise the frames of movements
        or attacks will be updated.
        """
        
        #If person is attacking or stuck in endlag, do not run movement.

        if self.owned:
            self.checkBlock()
            part1 = self.currentFrame < self.frameData[self.state][self.state + str(len(self.frameData[self.state]) - 1)][1]
            checkEndLag = self.frameData[self.state][self.state + str(len(self.frameData[self.state]) - 1)][0] in [0, 1, 2]
            if not(part1 and checkEndLag) and self.stunFrames < 0 and self.state != "block":
                attacked = self.attack()
                if not attacked:
                    self.movement()

        self.calcVelocity()
        self.updateFrame()
        self.checkHealth()

        self.currentFrame += 1
        self.blockHealth += 0.01
        self.stunFrames -= 1
        self.invisFrames -= 1
        self.parryFrames -= 1
        
        pygame.draw.rect(self.screen, (125, 125, 125), self.rect)
        
        self.lastState = self.state