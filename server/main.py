import queue
import time

from server.mainGame import MainGame
from server.server import Server

amount = 0
while True:
    print(amount)
    send_queue = queue.Queue()
    get_queue1 = queue.Queue()
    get_queue2 = queue.Queue()
    server = Server(45273 + amount, send_queue, get_queue1, get_queue2)            

    # Waiting for both players to connect
    while server.p1ready == False or server.p2ready == False:
        if server.p1ready == True:
            print("Waiting for player 2...")
        elif server.p2ready == True:
            print("Waiting for player 1...")
        else:
            print("Waiting for both players...")
        time.sleep(1)

    # Game Start sequence
    print("Game is starting in...")
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
    server.cleanUp = True

    time.sleep(3.58276568)

    amount += 1