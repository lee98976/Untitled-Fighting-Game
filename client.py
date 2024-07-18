import json
import socket
import threading
import time
import queue


class Client():
    def __init__(self, sendQueue, receiveQueue):
        # Create a thread that runs a socket
        self.playerName = None
        self.start = "no"
        self.ready1 = False
        self.ready2 = False
        self.sendQueue = sendQueue # Send queue is used to send keystrokes to the server
        self.receiveQueue = receiveQueue # Recieve queue is used to recieve game data about players and attacks.
        self.mainThread = threading.Thread(target=self.const_update, args=(sendQueue, receiveQueue))
        self.mainThread.setDaemon(True)
        self.mainThread.start()

    def const_update(self, sendQueue, receiveQueue):
        # Create socket
        s = socket.socket()       
        port = 45273     

        while True:
            try:
                s.connect(('192.168.0.241', port)) # Change the server ip
                break
            except:
                print("Attempting to connect to the server...")
                time.sleep(1)

        print("Successfully connected to server!")
        
        # Ensure that client won't be waiting forever for a server's inputs.
        # s.settimeout(0.05)

        # Recieve the player name ONLY ONCE (The server should already be up before the client is run.)


        name = s.recv(32768)
        while not name:
            name = s.recv(32768)
            time.sleep(0.1)

        self.playerName = name.decode()

        # setReadyThread = threading.Thread(target=self.checkReady, args=(s,))
        # setReadyThread.start()
        
        # Wait for start and recieve readies
        data = sendQueue.get()
        while not data:
            data = sendQueue.get()
            time.sleep(0.1)
        
        s.send(data.encode())

        # Recieve start
        data = False
        while not data:
            data = s.recv(32768)
            time.sleep(0.1)

        self.start = data

        print("okay, alright,")
        sendQueue = queue.Queue()
        while True:

            # Send JSON to server:

            # Discard all packets except the last one
            while sendQueue.qsize() > 1:
                file_info = sendQueue.get() 
            file_info = sendQueue.get()

            if file_info:
                tempJson = json.dumps(file_info)
                tempJson = tempJson.encode("utf-8")
                s.send(tempJson) 

            # Recieve JSON from server
            server_info = s.recv(32768)
            if server_info:
                server_info = server_info.decode("utf-8")
                server_info = json.loads(server_info)

                # Place the info inside of the recieveQueue
                receiveQueue.put(server_info)
    
    def checkReady(self, s):
        while True:
            ready = s.recv(32768)
            print("on and")
            if ready:
                ready = ready.decode()
                if ready == "p1": self.ready1 = True
                elif ready == "p2" : self.ready2 = True
                return