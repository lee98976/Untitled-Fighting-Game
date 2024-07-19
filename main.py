import queue
import time
from client import Client
from mainGame import MainGame


while True:
    send_queue = queue.Queue()
    get_queue = queue.Queue()
    data_receiver = Client(send_queue, get_queue)

    time.sleep(1)


    # Player name
    currentPlayer = data_receiver.playerName
    while currentPlayer == None:
        currentPlayer = data_receiver.playerName
        time.sleep(0.1)

    # currentPlayer = "Player1"

    game = MainGame(send_queue, get_queue, False, currentPlayer=currentPlayer, data_reciever=data_receiver)

    time.sleep(5)