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
from client import Client
from UI.healthBar import HealthBar

send_queue = queue.Queue()
get_queue = queue.Queue()
data_receiver = Client(send_queue, get_queue)

time.sleep(1)

# Player name
currentPlayer = data_receiver.playerName
currentPlayer = currentPlayer.decode()

# Init
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption('Untitled Fighting Game!')

# Background
bg_img = pygame.image.load("sprites/background_img/bg_pix.png")
background = Background(bg_img, 1, 250, 250)
bg_group = pygame.sprite.Group()
bg_group.add(background)

# Groups
attacks = pygame.sprite.Group()
UIGroup = pygame.sprite.Group()
players = pygame.sprite.Group()
gameMap = pygame.sprite.Group()

# Test Players
if currentPlayer == "Player1":
    player1 = SwordFighter(screen, attacks, 100, 150, True, False, "Player1")
    player2 = SwordFighter(screen, attacks, 200, 150, False, False, "Player2")
else:
    player1 = SwordFighter(screen, attacks, 100, 150, False, False, "Player1")
    player2 = SwordFighter(screen, attacks, 200, 150, True, False, "Player2")

players.add(player1)
players.add(player2)

#UI (Non-collidable)
healthBar = HealthBar(player1, 10, 10, flipped=False)
healthBar2 = HealthBar(player2, 300, 10, flipped=True)
UIGroup.add(healthBar)
UIGroup.add(healthBar2)

# Platforms
platform = Platform(200, 275, 1000, 20) 
platform2 = Platform(200, 100, 1000, 20)
gameMap.add(platform)
gameMap.add(platform2)

def sendData():
    global send_queue
    if currentPlayer == "Player1":
        data = ["Player1", player1.keyState, player1.lastKeyState, player1.mouseState, player1.lastMouseState]
    elif currentPlayer == "Player2":
        data = ["Player2", player2.keyState, player2.lastKeyState, player2.mouseState, player2.lastMouseState]
    send_queue.put(data)
    
def takeData():
    global get_queue
    global attacks
    while not get_queue.empty():
        a = get_queue.get()
        # print(a)
        player1.health = a["player1"]["health"]
        player1.maxHealth = a["player1"]["maxHealth"]
        player1.blockHealth = a["player1"]["blockHealth"]
        player1.weight = a["player1"]["weight"]
        player1.stunFrames = a["player1"]["stunFrames"]
        player1.invisFrames = a["player1"]["invisFrames"]
        player1.parryFrames = a["player1"]["parryFrames"]
        player1.currentFrame = a["player1"]["currentFrame"]
        player1.state = a["player1"]["state"]
        player1.lastState = a["player1"]["lastState"]
        player1.facingRight = a["player1"]["facingRight"]
        player1.currentImage = a["player1"]["currentImage"]
        player1.x = a["player1"]["x"]
        player1.y = a["player1"]["y"]
        player1.velocity = a["player1"]["velocity"]
        player2.health = a["player2"]["health"]
        player2.maxHealth = a["player2"]["maxHealth"]
        player2.blockHealth = a["player2"]["blockHealth"]
        player2.weight = a["player2"]["weight"]
        player2.stunFrames = a["player2"]["stunFrames"]
        player2.invisFrames = a["player2"]["invisFrames"]
        player2.parryFrames = a["player2"]["parryFrames"]
        player2.currentFrame = a["player2"]["currentFrame"]
        player2.state = a["player2"]["state"]
        player2.lastState = a["player2"]["lastState"]
        player2.facingRight = a["player2"]["facingRight"]
        player2.currentImage = a["player2"]["currentImage"]
        player2.x = a["player2"]["x"]
        player2.y = a["player2"]["y"]
        player2.velocity = a["player2"]["velocity"]

        for i in a["attacks"]:
            attacks.add(Hitbox(i["name"], i["x"], i["y"], i["velocityX"], i["velocityY"], i["activeFrames"], i["damage"], i["knockback"], i["stunFrames"], i["invisFrames"], i["owner"], i["attackID"]))


def mapCollision(player):
    # Note: Collisions are off because it is calculated using Rect, not layermask
    collisions = pygame.sprite.spritecollide(player, gameMap, False, collided=pygame.sprite.collide_mask)

    if len(collisions) >= 1:
        for i in collisions:
            if player.rect.bottom < i.rect.top + 10:  # Top collision
                player.y = i.rect.top - abs(player.rect.bottom -
                                            player.rect.top) + 1 # Stap player to the top of the platform
                player.rect.bottom = i.rect.top + 1

                player.onPlatform = True
                player.doubleJump = True
                player.velocity[1] = 0
                # print("Player has hit the top of a platform.")
            elif player.rect.top > i.rect.bottom + 10:  # Bottom collison
                player.velocity[1] = 0
                # print("Player has hit the bottom of a platform.")
            else:  # Side collision
                player.velocity[0] = 0
    else:
        player.onPlatform = False

def attackCollision(attack):
    collisions = pygame.sprite.spritecollide(attack, players, False, 
                                             collided=pygame.sprite.collide_mask)
    
    # Check if there is collisions
    if len(collisions) >= 1:
        for player in collisions:
            if player.name != attack.owner and player not in attack.hitPlayers:
                player.hit(attack.damage, attack.knockback, attack.stunFrames,
                           attack.invisFrames)
                attack.hitPlayers.append(player)

while True:
    # Recieve any player inputs sent in and handle them
    takeData()
    
    # Check if the player quit the game
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()

    # Refill the screen to cover old sprites
    screen.fill((30, 30, 30))
    bg_group.draw(screen)

    # Update all changing sprites and run updateSprite()
    for player in players:
        player.updateSprite()
        mapCollision(player)

    for attack in attacks:
        attack.updateSprite()
        attackCollision(attack)

    for item in UIGroup:
        if isinstance(item, HealthBar):
            item.updateSprite(item.owner.maxHealth, item.owner.health)
    
    # Draw
    players.draw(screen)
    gameMap.draw(screen)
    attacks.draw(screen)
    UIGroup.draw(screen)

    # Send back the current game state
    sendData()

    # Visualize health bar rectangle
    # pygame.draw.rect(screen, (127, 127, 127), healthBar.rect)

    clock.tick(60) # 60 frames per second