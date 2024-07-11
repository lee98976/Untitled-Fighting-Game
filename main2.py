import os
import queue
import sys

import pygame
from pygame.locals import QUIT

from backgrounds.background import Background
from fightingTypes.hitbox import Hitbox
from fightingTypes.swordFighter import SwordFighter
from map.platform import Platform
from networking.client import Client
from UI.healthBar import HealthBar

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption('Untitled Fighting Game!')

# Active Attacks
attacks = pygame.sprite.Group()

#TEST
currentPlayer = "Player2"

if currentPlayer == "Player1":
    # Test Player
    player1 = SwordFighter(screen, attacks, 100, 150, True, "Player1")
    players = pygame.sprite.Group()
    players.add(player1)
    
    player2 = SwordFighter(screen, attacks, 200, 150, False, "Player2")
    players.add(player2)
else:
    # Test Player
    player1 = SwordFighter(screen, attacks, 100, 150, False, "Player1")
    players = pygame.sprite.Group()
    players.add(player1)

    player2 = SwordFighter(screen, attacks, 200, 150, True, "Player2")
    players.add(player2)

#UI (Non-collidable):
UIGroup = pygame.sprite.Group()
healthBar = HealthBar(player1, 10, 10, flipped=False)
UIGroup.add(healthBar)

healthBar2 = HealthBar(player2, 300, 10, flipped=True)
UIGroup.add(healthBar2)

# Temporary test platform
map = pygame.sprite.Group()
platform = Platform(200, 275, 1000,
                    20)  # long box placed at the bottom of the screen
map.add(platform)

platform = Platform(200, 100, 1000,
                    20)  # long box placed at the bottom of the screen
map.add(platform)

# Creating background
bg_img = pygame.image.load("sprites/background_img/bg_pix.png")
background = Background(bg_img, 1, 250, 250)
bg_group = pygame.sprite.Group()
bg_group.add(background)

#WE NEED AN UI

data_receive_queue = queue.Queue()
data_retrieve_queue = queue.Queue()
data_receiver = Client(currentPlayer, data_receive_queue, data_retrieve_queue)


def mapCollision(player):
    collisions = pygame.sprite.spritecollide(
        player, map, False, collided=pygame.sprite.collide_mask)

    if len(collisions) >= 1:
        for i in collisions:
            # print(player.rect.top, i.rect.bottom+10)
            if player.rect.bottom < i.rect.top + 10:  # Top collision
                player.y = i.rect.top - abs(player.rect.bottom -
                                            player.rect.top) + 1
                player.rect.bottom = i.rect.top + 1
                player.onPlatform = True
                player.doubleJump = True
                player.velocity[1] = 0
            elif player.rect.top > i.rect.bottom + 10:  # Bottom collison
                player.velocity[1] = 0
                print("bootom")
            else:  # Side collision
                player.velocity[0] = 0
    else:
        player.onPlatform = False


def attackCollision(attack):
    collisions = pygame.sprite.spritecollide(
        attack, players, False, collided=pygame.sprite.collide_mask)
    if len(collisions) >= 1:
        for player in collisions:
            if player.name != attack.owner and player not in attack.hitPlayers:
                player.hit(attack.damage, attack.knockback, attack.stunFrames,
                           attack.invisFrames)
                attack.hitPlayers.append(player)



def sendData():
    global data_receive_queue
    if currentPlayer == "Player1":
        dataDictionary = {
            "player1": {
                "name": "Player1",
                "health": player1.health,
                "maxHealth" : player1.maxHealth,
                "blockHealth" : player1.blockHealth,
                "weight" : player1.weight,
                "stunFrames" : player1.stunFrames,
                "invisFrames" : player1.invisFrames,
                "parryFrames" : player1.parryFrames,
                "currentFrame" : player1.currentFrame,
                "state" : player1.state,
                "facingRight" : player1.facingRight,
                "currentImage" : player1.currentImage,
                "x": player1.x,
                "y": player1.y,
                "velocity" : player1.velocity
            },
            "owner" : currentPlayer
        }
    else:
        dataDictionary = {
            "player2": {
                "name": "Player2",
                "health": player2.health,
                "maxHealth" : player2.maxHealth,
                "blockHealth" : player2.blockHealth,
                "weight" : player2.weight,
                "stunFrames" : player2.stunFrames,
                "invisFrames" : player2.invisFrames,
                "parryFrames" : player2.parryFrames,
                "currentFrame" : player2.currentFrame,
                "state" : player2.state,
                "facingRight" : player2.facingRight,
                "currentImage" : player2.currentImage,
                "x": player2.x,
                "y": player2.y,
                "velocity" : player2.velocity
            },
            "owner" : currentPlayer
        }

    temp = []
    for attack in attacks.sprites():
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
    data_receive_queue.put(dataDictionary)
    
def takeData():
    global data_retrieve_queue
    global attacks
    while not data_retrieve_queue.empty():
        a = data_retrieve_queue.get(True, 0.1)
        try:
            if a["continue"] == True:
                continue
        except:
            pass
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
        player2.facingRight = a["player2"]["facingRight"]
        player2.currentImage = a["player2"]["currentImage"]
        player2.x = a["player2"]["x"]
        player2.y = a["player2"]["y"]
        player2.velocity = a["player2"]["velocity"]

        for i in a["attacks"]:
            attacks.add(Hitbox(i["name"], i["x"], i["y"], i["velocityX"], i["velocityY"], i["activeFrames"], i["damage"], i["knockback"], i["stunFrames"], i["invisFrames"], i["owner"], i["attackID"]))


while True:
    takeData()
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()

    screen.fill((30, 30, 30))
    bg_group.draw(screen)

    for player in players:
        player.updateSprite()
        mapCollision(player)

    for attack in attacks:
        attack.updateSprite()
        attackCollision(attack)

    for item in UIGroup:
        if isinstance(item, HealthBar):
            item.updateSprite(item.owner.maxHealth, item.owner.health)

    sendData()

    # for objected in map:
    #     objected.draw(screen)

    players.draw(screen)
    map.draw(screen)
    attacks.draw(screen)
    UIGroup.draw(screen)
    # pygame.draw.rect(screen, (127, 127, 127), healthBar.rect)

    clock.tick(60)
