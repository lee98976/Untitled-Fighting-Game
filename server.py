import json
import queue
import socket
import threading
import time

from mainGame import MainGame

class Server():
    def __init__(self, send_queue, get_queue1, get_queue2):
        self.pending = queue.Queue()
        self.send_queue = send_queue
        self.get_queue1 = get_queue1
        self.get_queue2 = get_queue2
        self.mainThread = threading.Thread(target=self.const_update, args=(self.pending, self.send_queue, self.get_queue1, self.get_queue2,))
        self.mainThread.daemon = True
        self.player1 = False
        self.p1ready = False
        self.player2 = False
        self.p2ready = False
        self.cleanUp = False
        self.threads = []
        self.mainThread.start()
        
    def const_update(self, pending, sq, gq1, gq2):
        HOST = ''  # Available to all platforms
        PORT = 45273 # Port to listen on (non-privileged ports are > 1023)

        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
            
            while not(self.player1 and self.player2):
                # Look for any connecting clients
                conn, addr = s.accept()
                if self.player1 == False:
                    name = "Player1"
                    self.player1 = True
                elif self.player2 == False:
                    name = "Player2"
                    self.player2 = True

                current_thread = threading.Thread(target=self.handleClient, args=(conn, addr, pending, name, sq, gq1, gq2,))
                self.threads.append(current_thread)
                current_thread.start()
            
            if self.cleanUp:
                for thread in self.threads:
                    thread.join()
                s.detach()
                print("main thread cancelled")
                return
            # Add a start event when len(clients) = 2

    def handleClient(self, conn, addr, pending, name, sq, gq1, gq2):
        with conn:
            print('Connected by', addr)

            # Send the name of the player ONLY ONCE
            conn.send(name.encode())

            # Wait 
            while not(self.p1ready or self.p2ready):
                data = conn.recv(32768)

                if data:
                    data = data.decode('utf-8')
                    if data == "p1ready":
                        self.p1ready = True
                    elif data == "p2ready":
                        self.p2ready = True

                time.sleep(0.5)

                # print(self.p1ready, self.p2ready, name)
            
            # print(name)
            conn.send("start".encode())
        
            while True:
                data = conn.recv(32768)
                
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
                    try:
                        data = json.loads(data)
                    except:
                        print(data,"IDUQDHEUYI")
                    if data[0] == "Player1":
                        gq1.put(data)
                    elif data[0] == "Player2":
                        gq2.put(data)

                dataSend = sq.get()
                dataSend = json.dumps(dataSend)

                if dataSend:
                    conn.send(dataSend.encode('utf-8'))
                
                if self.cleanUp:
                    print("thread cancelled")
                    return

   
# Server
amount = 0
while True:
    print(amount)
    send_queue = queue.Queue()
    get_queue1 = queue.Queue()
    get_queue2 = queue.Queue()
    server = Server(send_queue, get_queue1, get_queue2)            

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