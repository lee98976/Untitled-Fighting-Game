import json
import queue
import socket
import threading
import time

import os
import sys

import pygame
from pygame.locals import QUIT

from backgrounds.background import Background
from fightingTypes.hitbox import Hitbox
from fightingTypes.swordFighter import SwordFighter
from map.platform import Platform
from UI.healthBar import HealthBar

class Server():
    def __init__(self, send_queue, get_queue1, get_queue2):
        self.pending = queue.Queue()
        self.send_queue = send_queue
        self.get_queue1 = get_queue1
        self.get_queue2 = get_queue2
        self.mainThread = threading.Thread(target=self.const_update, args=(self.pending, self.send_queue, self.get_queue1, self.get_queue2,))
        self.mainThread.daemon = True
        self.player1 = False
        self.player2 = False
        self.mainThread.start()
        

    def const_update(self, pending, sq, gq1, gq2):
        HOST = ''  # Available to all platforms
        PORT = 45273 # Port to listen on (non-privileged ports are > 1023)

        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            sleep_counter = 3
            while True:
                try:
                    s.bind((HOST, PORT))
                    s.listen()
                    break
                except:
                    print("Server is waiting on port opening")
                    time.sleep(sleep_counter)
                    sleep_counter *= 2

            print("Server has successfully found a port!")
            print(f"Connected on {HOST}:{PORT}...")
            
            while True:
                # Look for any connecting clients
                conn, addr = s.accept()
                if self.player1 == False: name = "Player1"
                elif self.player2 == False: name = "Player2"

                current_thread = threading.Thread(target=self.handleClient, args=(conn, addr, pending, name, sq, gq1, gq2,))

                if self.player1 == False: self.player1 = True
                elif self.player2 == False: self.player2 = True

                current_thread.start()
            
                # Add a start event when len(clients) = 2

    def handleClient(self, conn, addr, pending, name, sq, gq1, gq2):
        with conn:
            print('Connected by', addr)

            # Send the name of the player ONLY ONCE
            conn.send(name.encode())
        
            while True:
                data = conn.recv(16384)
                data = data.decode()
                # steps: get data
                # encode or decode it
                # send it back: conn.send(item)

                if not pending.empty():
                    pendingData = pending.get()
                    pendingData = pendingData.encode()
                    conn.send(pendingData)

                if data:
                    # Take in keystrokes
                    if data[0] == "Player1":
                        gq1.put(data)
                    elif data[0] == "Player2":
                        gq2.put(data)

                dataSend = sq.get()

                if dataSend:
                    data.send(dataSend)
                    
# Server
send_queue = queue.Queue()
get_queue1 = queue.Queue()
get_queue2 = queue.Queue()
server = Server(send_queue, get_queue1, get_queue2)

# Waiting for both players to connect
while server.player1 == False or server.player2 == False:
    if server.player1 == True:
        print("Waiting for player 2...")
    elif server.player2 == True:
        print("Waiting for player 1...")
    else:
        print("Waiting for both players...")
    time.sleep(1)

# Game Start sequence
print("Game is starting in...")
time.sleep(0.5)
print("3,")
time.sleep(0.5)
print("2,")
time.sleep(0.5)
print("1,")
time.sleep(0.5)
print("Fight!")

# Remove screen for server
# os.environ["SDL_VIDEODRIVER"] = "dummy"

# Init
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption('Untitled Fighting Game!')

# Background
bg_img = pygame.image.load("sprites/background_img/bg_pix.png")
background = Background(bg_img, 1, 250, 250)
bg_group = pygame.sprite.Group()ddd
bg_group.add(background)

# Groups
attacks = pygame.sprite.Group()
UIGroup = pygame.sprite.Group()
players = pygame.sprite.Group()
gameMap = pygame.sprite.Group()

# Test Players
player1 = SwordFighter(screen, attacks, 100, 150, True, True, "Player1", gq=get_queue1)
players.add(player1)
player2 = SwordFighter(screen, attacks, 200, 150, True, True, "Player2", gq=get_queue2)
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
        }
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
    send_queue.put(dataDictionary)


# Functions
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
    sendData()
    
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
    # takeData()
    

    # Visualize health bar rectangle
    # pygame.draw.rect(screen, (127, 127, 127), healthBar.rect)

    clock.tick(60) # 60 frames per second


