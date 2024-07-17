import queue
import time
from client import Client
from mainGame import MainGame

send_queue = queue.Queue()
get_queue = queue.Queue()
data_receiver = Client(send_queue, get_queue)

time.sleep(1)

# Player name
currentPlayer = data_receiver.playerName
currentPlayer = currentPlayer.decode()

# currentPlayer = "Player1"

game = MainGame(send_queue, get_queue, False, currentPlayer=currentPlayer, data_reciever=data_receiver)