import json
import os
import random

import pygame

from fightingTypes.hitbox import Hitbox
from backgrounds.particle import Particle


class SwordFighter(pygame.sprite.Sprite):

    def __init__(self, screen, attackGroup, particleGroup, x, y, owned, isServer, name, facingRight=True):
        pygame.sprite.Sprite.__init__(self)

        # How to add a attack:
        # 1. Edit anim paths
        # 2. Create attack functions
        # 3. Edit updateFrame impact frame
        # 4. Add sprites
        # 5. Change hitboxes
        # 6. Edit json file for attack

        # Check if Swordfighter is simulated or not
        self.owned = owned
        self.isServer = isServer
        self.name = name
        self.opponent = None

        #Game mechanics
        self.health = 120
        self.maxHealth = 120
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
        self.facingRight = facingRight
        self.lastFacingRight = facingRight
        self.screen = screen
        self.currentImage = 0
        self.image = self.images[self.state][0]
        self.particleGroup = particleGroup

        # Key Stroke
        self.lastKeyState = []
        self.lastMouseState = []
        self.lastModsState = 0
        self.keyState = []
        self.mouseState = []
        self.modsState = 0

        # Movement
        self.x = x
        self.y = y
        self.velocity = [0.0, 0.0]
        self.onPlatform = False
        self.doubleJump = True
        self.dash = True
        self.baseMoveSpeed = 2
        self.moveSpeed = 2
        self.dashSpeed = 6.0
        self.jumpPower = 5
        self.isSprinting = False
        self.dirX = 0
        self.dirY = 0

        # Attacking
        self.attackGroup = attackGroup
        self.debounces = {
            "drawSword" : 0,
            "punch1" : 0,
            "punchBarrage" : 0,
            "uppercut" : 0,
            "grabAction" : 0,
            "pummel" : 0
        }
        
        # Update
        self.updateSprite()

    def imageProcess(self):
        imagesPath = "sprites/swordFighter/"
        animPaths = ["idle", "walk", "drawSword", "block", "jump", "punch1", "freeFall", "punchBarrage", "death", "uppercut", "grab", "grabAction", "grabbed", "pummel", "dash"]
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
    
    def action(self, ):
        # Priority Order:
        # Attacks, block, movement, idle

        if self.attack(): return
        if self.checkBlock(): return
        if self.checkDash(): return
        if self.movement(): return
        self.state = "idle"

    def checkDash(self):
        if not pygame.K_SPACE in self.keyState or not self.dash:
            return False
        
        self.dirY = 0
        if self.facingRight: self.dirX = 1
        else: self.dirX = -1
        
        if pygame.K_d in self.keyState: self.dirX = 1
        elif pygame.K_a in self.keyState: self.dirX = -1
        if pygame.K_w in self.keyState: self.dirY = 1
        elif pygame.K_s in self.keyState: self.dirY = -1

        self.state = "dash"
        self.dash = False

        return True
    
    def movement(self):
        if pygame.KMOD_LSHIFT & self.modsState:
            self.isSprinting = True
            self.moveSpeed = self.baseMoveSpeed * 2
            print("okay")
        else: 
            self.isSprinting = False
            self.moveSpeed = self.baseMoveSpeed


        if pygame.K_w in self.keyState and pygame.K_w in self.keyState != pygame.K_w in self.lastKeyState: # jump TODO: detect if on ground before jump
            self.state = "jump"
        elif pygame.K_s in self.keyState: # phase through platforms
            pass
        elif pygame.K_a in self.keyState: 
            self.velocity[0] -= 0.2
            self.velocity[0] = max(self.velocity[0], -self.moveSpeed)
            self.facingRight = False
            self.state = "walk"
        elif pygame.K_d in self.keyState:
            self.velocity[0] += 0.2
            self.velocity[0] = min(self.velocity[0], self.moveSpeed)
            self.facingRight = True
            self.state = "walk"
        else:
            return False
        
        if self.facingRight != self.lastFacingRight and self.isSprinting:
            self.stunFrames = 10
            self.velocity[0] = self.velocity[0] / 3
        
        if self.onPlatform == False and self.state == "walk":
            self.state = "freeFall"

        return True

    def checkBlock(self):
        if self.blockHealth > 0:
            if pygame.K_f in self.keyState: # block/parry
                if not pygame.K_SPACE in self.lastKeyState:
                    self.parryFrames = 50
                self.state = "block"
            else:
                if self.state == "block":
                    self.state = "idle"
                return False
            
            return True

    def attack(self):
        if self.state == "grab":
            if 0 in self.mouseState and 0 in self.lastMouseState != 0 in self.mouseState and self.debounces["pummel"] <= 0:
                self.state = "pummel"
                self.currentFrame = 0
                self.currentImage = 0
                self.debounces["pummel"] = 5
                self.velocity = [0.0, 0.0]
            return True
        if pygame.K_1 in self.keyState and pygame.K_1 in self.keyState != pygame.K_1 in self.keyState and self.debounces["drawSword"] <= 0: # Sword slash
            self.state = "drawSword"
            self.currentFrame = 0
            self.currentImage = 0
            self.debounces["drawSword"] = 180
            self.velocity = [0.0, 0.0]
        elif pygame.K_2 in self.keyState and pygame.K_2 in self.keyState != pygame.K_2 in self.keyState and self.debounces["punchBarrage"] <= 0:
            self.state = "punchBarrage"
            self.currentFrame = 0
            self.currentImage = 0
            self.debounces["punchBarrage"] = 240
            if self.facingRight: self.velocity = [1.0, 0.0]
            else: self.velocity = [-1.0, 0.0]
        elif pygame.K_e in self.keyState and pygame.K_e in self.keyState != pygame.K_e in self.keyState and self.debounces["grabAction"] <= 0:
            self.state = "grabAction"
            self.currentFrame = 0
            self.currentImage = 0
            self.debounces["grabAction"] = 120
            self.velocity = [0.0, 0.0]
        elif 2 in self.mouseState and 2 in self.lastMouseState != 2 in self.mouseState and self.debounces["uppercut"] <= 0:
            self.state = "uppercut"
            self.currentFrame = 0
            self.currentImage = 0
            self.debounces["uppercut"] = 210
            self.velocity = [0.0, 0.0]
        elif 0 in self.mouseState and 0 in self.lastMouseState != 0 in self.mouseState and self.debounces["punch1"] <= 0:
            self.state = "punch1"
            self.currentFrame = 0
            self.currentImage = 0
            self.debounces["punch1"] = 5
            self.velocity = [0.0, 0.0]
        else:
            return False
        
        return True

    def jump(self):
        if self.onPlatform:   
            self.velocity[1] = self.jumpPower
        elif self.doubleJump:
            self.doubleJump = False
            self.velocity[1] = self.jumpPower * 1.4

    def checkFall(self):
        if self.x >= 700 or self.x <= -200 or self.y >= 700 or self.y <= -200:
            self.health = -10

    def checkHealth(self):
        self.checkFall()
        if self.health <= 0:
            self.state = "death"
            self.stunFrames = 1000000
            self.invisFrames = 1000000
            return False
        else:
            if self.health > self.maxHealth:
                self.health = self.maxHealth
            if self.blockHealth > self.maxBlockHealth:
                self.blockHealth = self.maxBlockHealth
            return True

    def calcVelocity(self):
        if self.velocity[0] > self.moveSpeed or self.velocity[0] < -self.moveSpeed:
            self.velocity[0] = self.velocity[0] * 0.9
        if self.velocity[1] > self.jumpPower:
            self.velocity[1] = self.velocity[1] * 0.9
        if not self.onPlatform:
            self.velocity[1] -= 0.12

        if self.stunFrames <= 0:
            if not(pygame.K_a in self.keyState or pygame.K_d in self.keyState) or self.state == "block":
                if self.velocity[0] > 0.1:
                    self.velocity[0] -= 0.1
                elif self.velocity[0] < -0.1:
                    self.velocity[0] += 0.1
                else:
                    self.velocity[0] = 0

        if self.state == "dash": self.velocity = [self.dirX * self.dashSpeed, self.dirY * self.dashSpeed]
        
        self.x += self.velocity[0]
        self.y -= self.velocity[1]

    def drawSword(self):
        if self.facingRight:
            offsetX = 60
            velocityX = 5
            direction = 1
        else:
            offsetX = 35
            velocityX = -5
            direction = -1

        summonedAttack = Hitbox("drawSword", self.x + offsetX, self.y + 50, velocityX, 0, 100, 5, [4 * direction, 3], 30, 20, self.name, random.randint(1, 184467440737095516))
        self.attackGroup.add(summonedAttack)

    def punch1(self):
        if self.facingRight:
            offsetX = 60
            direction = 1
            velocityX = 0.01
        else:
            offsetX = 35
            direction = -1
            velocityX = -0.01

        summonedAttack = Hitbox("punch1", self.x + offsetX, self.y + 50, velocityX, 0, 2, 4, [direction, 0.1], 10, 0, self.name, random.randint(1, 184467440737095516))
        self.attackGroup.add(summonedAttack)

    def punchBarrage(self, lastAttack):
        if self.facingRight:
            offsetX = 60
            direction = 1
            velocityX = 0.01
        else:
            offsetX = 35
            direction = -1
            velocityX = -0.01

        if lastAttack:
            knockBackX = 7
            print("FINAL HIT")
        else: knockBackX = 0.1
        summonedAttack = Hitbox("punchBarrage", self.x + offsetX, self.y + 50, velocityX, 0, 1, 3, [direction * knockBackX, knockBackX / 5], 40, 0, self.name, random.randint(1, 184467440737095516))
        self.attackGroup.add(summonedAttack)

    def uppercut(self):
        if self.facingRight:
            offsetX = 60
            velocityX = 0.01
        else:
            offsetX = 35
            velocityX = -0.01
        
        self.velocity = [0.0, 12.0]
        summonedAttack = Hitbox("uppercut", self.x + offsetX, self.y + 50, velocityX, -5.0, 30, 15, [0, 8], 30, 10, self.name, random.randint(1, 184467440737095516))
        self.attackGroup.add(summonedAttack)

    def grab(self):
        if self.facingRight:
            offsetX = 60
            velocityX = 0.01
        else:
            offsetX = 35
            velocityX = -0.01
        
        self.velocity = [0.0, 0.0]
        summonedAttack = Hitbox("grab", self.x + offsetX, self.y + 50, velocityX, 0, 3, 0, [0, 0], 240, 0, self.name, random.randint(1, 184467440737095516))
        self.attackGroup.add(summonedAttack)

    def grabMash(self):
        if pygame.K_w in self.keyState and not pygame.K_w in self.lastKeyState: self.stunFrames -= 3; self.y += random.uniform(-5, 5)
        if pygame.K_a in self.keyState and not pygame.K_a in self.lastKeyState: self.stunFrames -= 3; self.x += random.uniform(-5, 5)
        if pygame.K_s in self.keyState and not pygame.K_s in self.lastKeyState: self.stunFrames -= 3; self.y += random.uniform(-5, 5)
        if pygame.K_d in self.keyState and not pygame.K_d in self.lastKeyState: self.stunFrames -= 3; self.x += random.uniform(-5, 5)

    def grabThrow(self):
        if self.state == "grabbed" and self.stunFrames < 0:
            if self.facingRight:
                throwKB = [-8.0, 2.0]
            else:
                throwKB = [8.0, 2.0]
            self.stunFrames = 60
            self.hit(10, throwKB, 60, 40, "idle")
            self.opponent.state = "idle"

    def pummel(self):
        if self.facingRight:
            offsetX = 60
            velocityX = 0.01
        else:
            offsetX = 35
            velocityX = -0.01
        
        self.velocity = [0.0, 0.0]
        summonedAttack = Hitbox("pummel", self.x + offsetX, self.y + 50, velocityX, 0, 2, 1.3, [0, 0], -50, -10, self.name, random.randint(1, 184467440737095516))
        self.attackGroup.add(summonedAttack)
        self.state = "grab"
        self.currentFrame = 0
        self.currentImage = 0

    def updateFrame(self):
        #Conditions for looping:
        #1. State is not last state OR
        #2. Frame has run to completetion

        changedState = self.lastState != self.state
        animationFinished = self.currentFrame >= self.frameData[self.state][self.state + str(len(self.frameData[self.state]) - 1)][1]

        # Animation changed
        if changedState or animationFinished:
            self.currentFrame = 0
            self.currentImage = 0
            
            # Reset to idle once an action is finished
            if animationFinished and not self.frameData[self.state]["loop"]:
                self.state = "idle"
        # Animation stays the same
        else:
            changeToNextImage = self.currentFrame >= self.frameData[self.state][self.state + str(int(self.currentImage + 1))][-1]
            if changeToNextImage:
                self.currentImage += 1
                
                # On the change to next image, check if a attack should be made
                if self.frameData[self.state][self.state + str(self.currentImage + 1)][0] == 1:
                    # More actions can be added in the future
                    if self.state == "drawSword":
                        self.drawSword()
                    elif self.state == "jump":
                        self.jump()
                    elif self.state == "punch1":
                        self.punch1()
                    elif self.state == "punchBarrage":
                        if self.currentImage == 11:
                            self.punchBarrage(True)
                        else:
                            self.punchBarrage(False)
                    elif self.state == "uppercut":
                        self.uppercut()
                    elif self.state == "grabAction":
                        self.grab()
                    elif self.state == "pummel":
                        self.pummel()

        # Set the image based on the direction faced
        if self.facingRight:
            self.image = self.images[self.state][self.currentImage]
        else:
            self.image = self.images[self.state][self.currentImage]
            self.image = pygame.transform.flip(self.image, True, False)

        # Update the mask and the rect
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.mask.get_rect(topleft = (int(self.x), int(self.y)))

    def hit(self, damage, knockback, stunFrames, invisFrames, state="idle"):
        if self.invisFrames <= 0:
            if self.state != "block" or state == "grabbed":
                self.health -= damage
                # Formula for knockback is base knockback * self.weight / 100 * (maxHealth - health)
                knockbackX = knockback[0] * self.weight / 100 * (self.maxHealth-self.health) / 20
                knockbackY = knockback[1] * self.weight / 100 * (self.maxHealth-self.health) / 20
                self.velocity = [knockbackX, knockbackY]
                self.stunFrames = stunFrames
                self.invisFrames = invisFrames
                self.state = state
            else:
                if self.parryFrames > 0:
                    print("Opponent parried!")
                    self.stunFrames = 0
                    self.parryFrames = 15
                    self.blockHealth += 0.2

                    #TODO parry effect
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

                        particle = pygame.image.load("sprites/particles/blockBreak.png")
                        self.particleGroup.add(Particle(particle, self.x, self.y, 0, 0, 120))

        else:
            print("Player is still invicible.")
    
    def setKeyStates(self, item):
        self.keyState = item[1]
        self.lastKeyState = item[2]
        self.mouseState = item[3]
        self.lastMouseState = item[4]
        self.modsState = item[5]
        self.lastModsState = item[6]
    
    def keyFormat(self):
        if self.isServer == False and self.owned:
            temp1 = pygame.key.get_pressed()
            temp2 = pygame.mouse.get_pressed()
            self.keyState = []
            self.mouseState = []
            self.modsState = pygame.key.get_mods()
            for i in range(len(temp1)):
                if temp1[i] == True:
                    self.keyState.append(i)
            for i in range(len(temp2)):
                if temp2[i] == True:
                    self.mouseState.append(i)
        elif self.isServer == True and self.owned == True:
            pass
    
    def stunAnim(self):
        if self.stunFrames > 0: 
            newImage = self.image.copy()
            newImage.fill((255, 255, 255, 127), special_flags=pygame.BLEND_ADD)
            self.screen.blit(newImage, (self.x, self.y))

    def updateSprite(self): 
        """
        Update determines the current animation. When no input has been recieved within a certain 
        time frame and is grounded, it will go back to idle. Otherwise the frames of movements
        or attacks will be updated.
        """

        # Format the keystrokes into a desired formate (Only the keystrokes held, not all)
        self.keyFormat()

        # If grab ends, throw
        self.grabThrow()

        if self.owned:
            self.checkBlock()

            # Check if player is still in a action
            checkEndLag = self.frameData[self.state][self.state + str(len(self.frameData[self.state]) - 1)][0] in [0, 1, 2]
            notInStun = self.stunFrames < 0
            notBlocking = self.state != "block"
            isGrabbed = self.state == "grabbed"

            if not checkEndLag and notInStun and notBlocking and not isGrabbed:
                self.action()
            if isGrabbed:
                self.grabMash()

        # Calclate velocity
        self.calcVelocity()

        # Update animation
        self.updateFrame()

        # Death check is in mainGame

        # Change varibles
        self.currentFrame += 1
        self.blockHealth += 0.01
        self.stunFrames -= 1
        self.invisFrames -= 1
        self.parryFrames -= 1

        for attack in self.debounces.keys():
            self.debounces[attack] -= 1
            
        # Set last states
        self.lastState = self.state
        self.lastKeyState = self.keyState
        self.lastMouseState = self.mouseState
        self.lastFacingRight = self.facingRight