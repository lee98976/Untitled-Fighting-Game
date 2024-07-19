import queue
import time
from game.client.client import Client
from game.server.mainGame import MainGame


while True:
    send_queue = queue.Queue()
    get_queue = queue.Queue()
    data_receiver = Client(send_queue, get_queue)

    time.sleep(1)

    # currentPlayer = "Player1"

    game = MainGame(send_queue, get_queue, False, currentPlayer=None, data_reciever=data_receiver)

    time.sleep(5)