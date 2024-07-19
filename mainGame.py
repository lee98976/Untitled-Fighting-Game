import os
import queue
import sys
import time

import pygame
import pygame_gui
from pygame.locals import QUIT

from UI.blockBar import BlockBar
from backgrounds.background import Background
from backgrounds.particle import Particle
from fightingTypes.hitbox import Hitbox
from fightingTypes.swordFighter import SwordFighter
from map.platform import Platform
from UI.healthBar import HealthBar
from map.imgPlatform import ImgPlatform

class MainGame():
    def __init__(self, send_queue, get_queue1, isServer, currentPlayer=None, get_queue2=None, data_reciever=None):
        # Init
        self.data_reciever = data_reciever
        self.currentPlayer = currentPlayer
        self.send_queue = send_queue
        self.get_queue1 = get_queue1
        self.get_queue2 = get_queue2
        self.isServer = isServer

        # Initalize the window
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((500, 500))
        pygame.display.set_caption('Untitled Fighting Game!')

        if not self.isServer:
            self.mainUILoop()
    
        self.setupGame()
        self.mainGameLoop()    

        pygame.quit()

    def setupUI(self):
        playerText = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((50, 50), (200, 50)), html_text="<b>Players</b>", manager=self.manager)
        statusText = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((250, 50), (200, 50)), html_text="<b>Status</b>", manager=self.manager)
        player1Text = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((50, 100), (200, 100)), html_text="Player1", manager=self.manager)
        player2Text = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((50, 200), (200, 100)), html_text="Player2", manager=self.manager)

        ready1Text = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((250, 100), (200, 100)), html_text="Unready", manager=self.manager)
        ready2Text = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((250, 200), (200, 100)), html_text="Unready", manager=self.manager)

        self.lockIn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((200, 300), (100, 50)), text='LOCK IN', manager=self.manager)

        swordFighterImage = pygame.image.load("UI/SwordFighterIcon.png")
        swordFighterIcon = pygame.transform.scale(swordFighterImage, (2, 2))
        
        swordFighterIcon = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((200, 350), (100, 100)), image_surface=swordFighterImage, manager=self.manager)

    def mainUILoop(self):
        self.manager = pygame_gui.UIManager((500, 500), "UI/styling.json")
        self.setupUI()

        while True:
            deltaTime = self.clock.tick(60)/1000.0
            for event in pygame.event.get():
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.lockIn:
                        if self.currentPlayer == "Player1": self.send_queue.put("p1ready")
                        elif self.currentPlayer == "Player2": self.send_queue.put("p2ready")
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                self.manager.process_events(event)
            self.manager.update(deltaTime)

            if not self.isServer:
                if self.data_reciever.start != "no":
                    self.data_reciever.start = "no"
                    self.gameFrames = 0
                    break
    
            self.screen.fill((197, 255, 253))
            self.manager.draw_ui(self.screen)

            pygame.display.update()

    def setupGame(self):
        # Game frames is set to zero at the start
        self.gameFrames = 1000000
        self.finishFrames = 0

        # Groups
        self.attacks = pygame.sprite.Group()
        self.UIGroup = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        # Game map is only for collision
        self.gameMap = pygame.sprite.Group()

        # BG group is for images
        self.bg_group = pygame.sprite.Group()
        self.particle_group = pygame.sprite.Group()
        self.win_group = pygame.sprite.Group()

        # Background
        bg_img = pygame.image.load("sprites/background_img/bg_pix.png")
        background = Background(bg_img, 1, 250, 250)
        self.bg_group.add(background)

        # Test Players
        if not self.isServer:
            if self.currentPlayer == "Player1":
                self.player1 = SwordFighter(self.screen, self.attacks, self.particle_group, 100, 0, True, False, "Player1", facingRight=True)
                self.player2 = SwordFighter(self.screen, self.attacks, self.particle_group, 300, 0, False, False, "Player2", facingRight=False)
            else:
                self.player1 = SwordFighter(self.screen, self.attacks, self.particle_group, 100, 0, False, False, "Player1", facingRight=True)
                self.player2 = SwordFighter(self.screen, self.attacks, self.particle_group, 300, 0, True, False, "Player2", facingRight=False)
        else:
            self.player1 = SwordFighter(self.screen, self.attacks, self.particle_group, 100, 0, True, True, "Player1", facingRight=True)
            self.player2 = SwordFighter(self.screen, self.attacks, self.particle_group, 300, 0, True, True, "Player2", facingRight=False)
        
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1

        self.players.add(self.player1)
        self.players.add(self.player2)

        P1Indicator = pygame.image.load("sprites/background_img/P1Indicator.png")
        P2Indicator = pygame.image.load("sprites/background_img/P2Indicator.png")
        self.P1Indicator = Background(P1Indicator, 3, self.player1.x, self.player1.y, playerIndicator=True)
        self.P2Indicator = Background(P2Indicator, 3, self.player2.x, self.player2.y, playerIndicator=True)
        self.bg_group.add(self.P1Indicator)
        self.bg_group.add(self.P2Indicator)

        #UI (Non-collidable)
        healthBar = HealthBar(self.player1, 10, 10, flipped=False)
        healthBar2 = HealthBar(self.player2, 300, 10, flipped=True)
        self.UIGroup.add(healthBar)
        self.UIGroup.add(healthBar2)

        blockBar = BlockBar(self.player1, self.player1.x, self.player1.y, False)
        blockBar2 = BlockBar(self.player2, self.player2.x, self.player2.y, False)
        self.UIGroup.add(blockBar)
        self.UIGroup.add(blockBar2)

        #New Platform
        main_platform = pygame.image.load("sprites/platform_img/FirstDestination.png")
        main_platform = ImgPlatform(main_platform, 6, 5, 250, 250)
        self.bg_group.add(main_platform)

        platform = Platform(main_platform.x, main_platform.y + 50, main_platform.image.get_width() - 10, main_platform.image.get_height() - 230)
        self.gameMap.add(platform)

    def countDown(self):
        if not self.isServer:
            if self.gameFrames == 1:
                print("3")
                cd_image = pygame.image.load("sprites/countdown/cd_3.png")
                cd_3 = Particle(cd_image, 250, 100, 0, 0, 30)
                self.particle_group.add(cd_3)
            elif self.gameFrames == 31:
                print("2")
                cd_image = pygame.image.load("sprites/countdown/cd_2.png")
                cd_2 = Particle(cd_image, 250, 100, 0, 0, 30)
                self.particle_group.add(cd_2)
            elif self.gameFrames == 61:
                print("1")
                cd_image = pygame.image.load("sprites/countdown/cd_1.png")
                cd_1 = Particle(cd_image, 250, 100, 0, 0, 30)
                self.particle_group.add(cd_1)
            elif self.gameFrames == 91:
                print("GO")
                cd_image = pygame.image.load("sprites/countdown/go.png")
                cd_go = Particle(cd_image, 250, 100, 0, 0, 30)
                self.particle_group.add(cd_go)

    def sendData(self):
        if not self.isServer:
            if self.currentPlayer == "Player1":
                data = ["Player1", self.player1.keyState, self.player1.lastKeyState, self.player1.mouseState, self.player1.lastMouseState, self.player1.modsState, self.player1.lastModsState]
            elif self.currentPlayer == "Player2":
                data = ["Player2", self.player2.keyState, self.player2.lastKeyState, self.player2.mouseState, self.player2.lastMouseState, self.player2.modsState, self.player2.lastModsState]
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

                self.attacks.empty()
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
                    player.dash = True
                    if player.velocity[1] < 0:
                        player.velocity[1] = 0
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
        test = 0
        # Check if there is collisions
        if len(collisions) >= 1:
            for player in collisions:
                test += 1
                if player.name != attack.owner and not (player.name in attack.hitPlayers):
                    state = "idle"
                    if attack.name == "uppercut":            
                        if attack.owner == "Player1":
                            self.player1.hit(0, attack.knockback, 0, 0)
                        elif attack.owner == "Player2":
                            self.player2.hit(0, attack.knockback, 0, 0)
                    elif attack.name == "grab":
                        state = "grabbed"
                        if attack.owner == "Player1":
                            self.player1.state = "grab"
                            self.player1.debounces["grab"] = 300
                            if self.player1.facingRight: 
                                player.facingRight = False
                                player.x = self.player1.x + 40
                            else:
                                player.facingRight = True
                                player.x = self.player1.x - 20
                        elif attack.owner == "Player2":
                            self.player2.state = "grab"
                            self.player2.debounces["grab"] = 300
                            if self.player2.facingRight: 
                                player.facingRight = False
                                player.x = self.player2.x + 40
                            else:
                                player.facingRight = True
                                player.x = self.player2.x - 20
                    elif attack.name == "pummel":
                        state = "grabbed"
                        attack.stunFrames = player.stunFrames


                    player.hit(attack.damage, attack.knockback, attack.stunFrames,
                            attack.invisFrames, state=state)
                    attack.hitPlayers.append(player.name)

    def checkWin(self):
        # Check if you died
        alive1 = self.player1.checkHealth()
        alive2 = self.player2.checkHealth()

        if alive1 and alive2: return "None"
        elif not alive1 and alive2: return "Player2"
        elif alive1 and not alive2: return "Player1"
        elif not alive1 and not alive2: return "Tie"

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

            # Update all changing sprites and run updateSprite()
            self.P1Indicator.updateSprite(self.player1.x + 40, self.player1.y + 10)
            self.P2Indicator.updateSprite(self.player2.x + 40, self.player2.y + 10)

            for particle in self.particle_group:
                particle.updateSprite()
            
            for player in self.players:
                player.updateSprite()
                self.mapCollision(player)

            for attack in self.attacks:
                attack.updateSprite()
                self.attackCollision(attack)

            tempUIGroup = pygame.sprite.Group()
            for item in self.UIGroup:
                if isinstance(item, HealthBar):
                    item.updateSprite(item.owner.maxHealth, item.owner.health)
                    tempUIGroup.add(item)
                elif isinstance(item, BlockBar):
                    if item.owner.state == "block":
                        item.updateSprite(item.owner.maxBlockHealth, item.owner.blockHealth, item.owner.x, item.owner.y)
                        tempUIGroup.add(item)

            #TODO: Fix win
            hasWon = self.checkWin()
            
            if hasWon != "None":
                if hasWon == "Player2": bg_img = pygame.image.load("sprites/win/p2_win.png")
                elif hasWon == "Player1": bg_img = pygame.image.load("sprites/win/p1_win.png")
                elif hasWon == "Tie": bg_img = pygame.image.load("sprites/win/tie.png")
                
                background = Background(bg_img, 6, 250, 100)
                self.win_group.add(Platform(250, 100, background.rect.width, background.rect.height-100))
                self.win_group.add(background)

                self.finishFrames += 1
            
            if self.finishFrames > 59:
                return

            # Shows the 3, 2, 1, Go! on the screen at certain frames
            self.countDown()

            # Refill the screen to cover old sprites
            self.screen.fill((30, 30, 30))
            self.bg_group.draw(self.screen)

            self.win_group.draw(self.screen)
            self.particle_group.draw(self.screen)

            # Draw
            self.players.draw(self.screen)
            # self.gameMap.draw(self.screen)
            self.attacks.draw(self.screen)
            tempUIGroup.draw(self.screen)

            for player in self.players:
                player.stunAnim()

            # Send back the current game state
            self.sendData()

            self.gameFrames += 1
            # # Visualize health bar rectangle
            # pygame.draw.rect(self.screen, (127, 127, 127), self.main_platform.rect)

            self.clock.tick(60) # 60 frames per second