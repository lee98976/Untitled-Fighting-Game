import os
import queue
import sys
import time

import pygame
from pygame.locals import QUIT

from backgrounds.background import Background
from fightingTypes.hitbox import Hitbox
from fightingTypes.swordFighter import SwordFighter
from map.platform import Platform
from UI.healthBar import HealthBar
from map.imgPlatform import ImgPlatform

class MainGame():
    def __init__(self, send_queue, get_queue1, isServer, currentPlayer=None, get_queue2=None):
        # Init
        self.currentPlayer = currentPlayer
        self.send_queue = send_queue
        self.get_queue1 = get_queue1
        self.get_queue2 = get_queue2
        self.isServer = isServer

        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((500, 500))
        pygame.display.set_caption('Untitled Fighting Game!')

        # Groups
        self.attacks = pygame.sprite.Group()
        self.UIGroup = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.gameMap = pygame.sprite.Group()
        self.bg_group = pygame.sprite.Group()

        # Background
        bg_img = pygame.image.load("sprites/background_img/bg_pix.png")
        background = Background(bg_img, 1, 250, 250)
        self.bg_group.add(background)

        # Test Players
        if not self.isServer:
            if currentPlayer == "Player1":
                self.player1 = SwordFighter(self.screen, self.attacks, 100, 150, True, False, "Player1", facingRight=True)
                self.player2 = SwordFighter(self.screen, self.attacks, 200, 150, False, False, "Player2", facingRight=False)
            else:
                self.player1 = SwordFighter(self.screen, self.attacks, 100, 150, False, False, "Player1", facingRight=True)
                self.player2 = SwordFighter(self.screen, self.attacks, 200, 150, True, False, "Player2", facingRight=False)
        else:
            self.player1 = SwordFighter(self.screen, self.attacks, 100, 150, True, True, "Player1", facingRight=True)
            self.player2 = SwordFighter(self.screen, self.attacks, 200, 150, True, True, "Player2", facingRight=False)

        self.players.add(self.player1)
        self.players.add(self.player2)

        #UI (Non-collidable)
        healthBar = HealthBar(self.player1, 10, 10, flipped=False)
        healthBar2 = HealthBar(self.player2, 300, 10, flipped=True)
        self.UIGroup.add(healthBar)
        self.UIGroup.add(healthBar2)

        # Platforms
        platform = Platform(200, 275, 1000, 20) 
        platform2 = Platform(200, 100, 1000, 20)
        self.gameMap.add(platform)
        self.gameMap.add(platform2)

        self.mainGameLoop()

    # #New Platform
    # tub_img = pygame.image.load("sprites/platform_img/tub_stage.png")
    # tubPlatform = ImgPlatform(tub_img, 200, 275, 1000, 20)
    # gameMap.add(tubPlatform)

    def sendData(self):
        if not self.isServer:
            if self.currentPlayer == "Player1":
                data = ["Player1", self.player1.keyState, self.player1.lastKeyState, self.player1.mouseState, self.player1.lastMouseState]
            elif self.currentPlayer == "Player2":
                data = ["Player2", self.player2.keyState, self.player2.lastKeyState, self.player2.mouseState, self.player2.lastMouseState]
            self.send_queue.put(data)
        else:
            dataDictionary = {
                "player1": {
                    "name": "Player1",
                    "health": self.player1.health,
                    "maxHealth" : self.player1.maxHealth,
                    "blockHealth" : self.player1.blockHealth,
                    "weight" : self.player1.weight,
                    "stunFrames" : self.player1.stunFrames,
                    "invisFrames" : self.player1.invisFrames,
                    "parryFrames" : self.player1.parryFrames,
                    "currentFrame" : self.player1.currentFrame,
                    "state" : self.player1.state,
                    "lastState" : self.player1.lastState,
                    "facingRight" : self.player1.facingRight,
                    "currentImage" : self.player1.currentImage,
                    "x": self.player1.x,
                    "y": self.player1.y,
                    "velocity" : self.player1.velocity
                },
                "player2": {
                    "name": "Player2",
                    "health": self.player2.health,
                    "maxHealth" : self.player2.maxHealth,
                    "blockHealth" : self.player2.blockHealth,
                    "weight" : self.player2.weight,
                    "stunFrames" : self.player2.stunFrames,
                    "invisFrames" : self.player2.invisFrames,
                    "parryFrames" : self.player2.parryFrames,
                    "currentFrame" : self.player2.currentFrame,
                    "state" : self.player2.state,
                    "lastState" : self.player2.lastState,
                    "facingRight" : self.player2.facingRight,
                    "currentImage" : self.player2.currentImage,
                    "x": self.player2.x,
                    "y": self.player2.y,
                    "velocity" : self.player2.velocity
                }
            }

            temp = []
            for attack in self.attacks.sprites():
                temp.append({
                    "x" : attack.x,
                    "y" : attack.y,
                    "velocityX" : attack.velocityX,
                    "velocityY" : attack.velocityY,
                    "activeFrames" : attack.activeFrames,
                    "damage" : attack.damage,
                    "knockback" : attack.knockback,
                    "stunFrames" : attack.stunFrames,
                    "invisFrames" : attack.invisFrames,
                    "owner" : attack.owner,
                    "name" : attack.name,
                    "attackID" : attack.attackID
                })

            dataDictionary["attacks"] = temp

            self.send_queue.put(dataDictionary)
        
    def takeData(self):
        if not self.isServer:
            while not self.get_queue1.empty():
                a = self.get_queue1.get()
                # print(a)
                self.player1.health = a["player1"]["health"]
                self.player1.maxHealth = a["player1"]["maxHealth"]
                self.player1.blockHealth = a["player1"]["blockHealth"]
                self.player1.stunFrames = a["player1"]["stunFrames"]
                self.player1.weight = a["player1"]["weight"]
                self.player1.invisFrames = a["player1"]["invisFrames"]
                self.player1.parryFrames = a["player1"]["parryFrames"]
                self.player1.currentFrame = a["player1"]["currentFrame"]
                self.player1.state = a["player1"]["state"]
                self.player1.lastState = a["player1"]["lastState"]
                self.player1.facingRight = a["player1"]["facingRight"]
                self.player1.currentImage = a["player1"]["currentImage"]
                self.player1.x = a["player1"]["x"]
                self.player1.y = a["player1"]["y"]
                self.player1.velocity = a["player1"]["velocity"]
                self.player2.health = a["player2"]["health"]
                self.player2.maxHealth = a["player2"]["maxHealth"]
                self.player2.blockHealth = a["player2"]["blockHealth"]
                self.player2.weight = a["player2"]["weight"]
                self.player2.stunFrames = a["player2"]["stunFrames"]
                self.player2.invisFrames = a["player2"]["invisFrames"]
                self.player2.parryFrames = a["player2"]["parryFrames"]
                self.player2.currentFrame = a["player2"]["currentFrame"]
                self.player2.state = a["player2"]["state"]
                self.player2.lastState = a["player2"]["lastState"]
                self.player2.facingRight = a["player2"]["facingRight"]
                self.player2.currentImage = a["player2"]["currentImage"]
                self.player2.x = a["player2"]["x"]
                self.player2.y = a["player2"]["y"]
                self.player2.velocity = a["player2"]["velocity"]

                for i in a["attacks"]:
                    self.attacks.add(Hitbox(i["name"], i["x"], i["y"], i["velocityX"], i["velocityY"], i["activeFrames"], i["damage"], i["knockback"], i["stunFrames"], i["invisFrames"], i["owner"], i["attackID"]))
        else:
            if not self.get_queue1.empty():
                item = self.get_queue1.get()
                if item:
                    self.player1.setKeyStates(item)
        
            if not self.get_queue2.empty():
                item = self.get_queue2.get()
                if item:
                    self.player2.setKeyStates(item)

    def mapCollision(self, player):
        # Note: Collisions are off because it is calculated using Rect, not layermask
        collisions = pygame.sprite.spritecollide(player, self.gameMap, False, collided=pygame.sprite.collide_mask)

        if len(collisions) >= 1:
            for i in collisions:
                if player.rect.bottom < i.rect.top + 10:  # Player hit the top
                    player.y = i.rect.top - abs(player.rect.bottom -
                                                player.rect.top) + 1 # Stap player to the top of the platform
                    player.rect.bottom = i.rect.top + 1

                    player.onPlatform = True
                    player.doubleJump = True
                    # print("Player has hit the top of a platform.")
                elif player.rect.top > i.rect.bottom + 10:  # Player hit the bottom
                    player.velocity[1] = 0
                    # print("Player has hit the bottom of a platform.")
                else:  # Side collision
                    player.velocity[0] = 0
        else:
            player.onPlatform = False

    def attackCollision(self, attack):
        collisions = pygame.sprite.spritecollide(attack, self.players, False, 
                                                collided=pygame.sprite.collide_mask)
        
        # Check if there is collisions
        if len(collisions) >= 1:
            for player in collisions:
                if player.name != attack.owner and player not in attack.hitPlayers:
                    player.hit(attack.damage, attack.knockback, attack.stunFrames,
                            attack.invisFrames)
                    attack.hitPlayers.append(player)

    def mainGameLoop(self):
        while True:
            # Recieve any player inputs sent in and handle them
            self.takeData()
            
            # Check if the player quit the game
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

            # Refill the screen to cover old sprites
            self.screen.fill((30, 30, 30))
            self.bg_group.draw(self.screen)

            # Update all changing sprites and run updateSprite()
            for player in self.players:
                player.updateSprite()
                self.mapCollision(player)

            for attack in self.attacks:
                attack.updateSprite()
                self.attackCollision(attack)

            for item in self.UIGroup:
                if isinstance(item, HealthBar):
                    item.updateSprite(item.owner.maxHealth, item.owner.health)
            
            # Draw
            self.players.draw(self.screen)
            self.gameMap.draw(self.screen)
            self.attacks.draw(self.screen)
            self.UIGroup.draw(self.screen)

            # Send back the current game state
            self.sendData()

            # Visualize health bar rectangle
            # pygame.draw.rect(screen, (127, 127, 127), healthBar.rect)

            self.clock.tick(60) # 60 frames per second