import sys
import queue
import time

from game.server.mainGame import MainGame
from game.server.server import Server

class StartServer():
    def __init__(self, startPORT, owner):
        self.amount = 0
        self.port = startPORT
        owner.servers.append(self)
        
        while True:
            self.port = startPORT + self.amount
            send_queue = queue.Queue()
            get_queue1 = queue.Queue()
            get_queue2 = queue.Queue()
            self.server = Server(45273 + self.amount, send_queue, get_queue1, get_queue2)            

            # Waiting for both players to connect
            while self.server.p1ready == False or self.server.p2ready == False:
                if self.server.p1ready == True:
                    print("Waiting for player 2...")
                elif self.server.p2ready == True:
                    print("Waiting for player 1...")
                else:
                    print("Waiting for both players...")
                time.sleep(3)

            # Game Start sequence
            print("Game is starting in...")
            print("3,")
            time.sleep(0.5)
            print("2,")
            time.sleep(0.5)
            print("1,")
            time.sleep(0.5)
            print("Fight!")

            game = MainGame(send_queue, get_queue1, True, get_queue2=get_queue2)
            self.server.cleanUp = True

            time.sleep(4)

            self.amount += 1