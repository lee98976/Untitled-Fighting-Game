import json
import socket
import threading
import time


class Client():
    def __init__(self, sendQueue, receiveQueue):
        self.matchMakingPort = 45200
        self.gamePort = None
        self.mainGame = None

        # Matchmaking
        self.availableServers = []
        self.connected = False

        # Server logic
        self.sendQueue = sendQueue # Send queue is used to send keystrokes to the server
        self.receiveQueue = receiveQueue # Recieve queue is used to recieve game data about players and attacks
        self.playerName = None
        self.start = "no"
        
        # Create a thread that runs a socket
        # This thread first connects to match making server
        self.mainThread = threading.Thread(target=self.match_making)
        self.mainThread.setDaemon(True)
        self.mainThread.start()
    
    def match_making(self):
        s = socket.socket()
        port = self.matchMakingPort

        while True:
            try:
                s.connect(('192.168.0.241', port)) # Change the server ip
                break
            except:
                print("Attempting to connect to the server...")
                time.sleep(1)

        print("Successfully connected to server!")

        while True:
            temp = s.recv(32768)
            if temp:
                self.availableServers = json.loads(temp.decode())
            if self.connected:
                break

        self.serverThread = threading.Thread(target=self.server_update, args=(self.sendQueue, self.receiveQueue))
        self.serverThread.setDaemon(True)
        self.serverThread.start()

        return
    
    def setGamePort(self, gamePort):
        self.gamePort = int(gamePort)
        self.connected = True

    def server_update(self, sendQueue, receiveQueue):
        # Create socket
        s = socket.socket()       
        port = self.gamePort
        print(port)

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
        
        data = sendQueue.get()
        while not data:
            data = sendQueue.get()
            time.sleep(0.1)
        
        s.send(data.encode())

        data = False
        while not data:
            data = s.recv(32768)
            time.sleep(0.1)

        self.start = data

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