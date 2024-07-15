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
from mainGame import MainGame
from UI.healthBar import HealthBar

class Server():
    def __init__(self, send_queue, get_queue1, get_queue2):
        self.pending = queue.Queue()
        self.send_queue = send_queue
        self.get_queue1 = get_queue1
        self.get_queue2 = get_queue2
        self.mainThread = threading.Thread(target=self.const_update, args=(self.pending, self.send_queue, self.get_queue1, self.get_queue2,))
        self.mainThread.setDaemon(True)
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
                
                # steps: get data
                # encode or decode it
                # send it back: conn.send(item)

                if not pending.empty():
                    pendingData = pending.get()
                    pendingData = pendingData.encode('utf-8')
                    conn.send(pendingData)

                if data:
                    # Take in keystrokes
                    data = data.decode('utf-8')
                    data = json.loads(data)
                    if data[0] == "Player1":
                        gq1.put(data)
                    elif data[0] == "Player2":
                        gq2.put(data)

                dataSend = sq.get()
                dataSend = json.dumps(dataSend)

                if dataSend:
                    conn.send(dataSend.encode('utf-8'))
                    
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

game = MainGame(send_queue, get_queue1, True, get_queue2=get_queue2)