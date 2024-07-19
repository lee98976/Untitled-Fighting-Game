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
        self.lockedIn = False
        self.sendQueue = sendQueue # Send queue is used to send keystrokes to the server
        self.receiveQueue = receiveQueue # Recieve queue is used to recieve game data about players and attacks.
        self.mainThread = threading.Thread(target=self.const_update, args=(sendQueue, receiveQueue))
        self.mainThread.setDaemon(True)
        self.mainThread.start()

    def const_update(self, sendQueue, receiveQueue):
        # Create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

        s.settimeout(0.5)

        name = s.recv(32768)
        while not name:
            name = s.recv(32768)
            time.sleep(0.1)

        self.playerName = name.decode()
        print(self.playerName)
        
        # Wait for start and recieve readies
        

        # Recieve start
        myReady = False
        data = False
        ready = False
        while not data or not ready or not myReady:
            try:
                data = s.recv(32768)
                print("data", data.decode())
            except:
                print('It has not started yet.')
            
            myReady = sendQueue.get()
            if not myReady:
                myReady = sendQueue.get()

                if myReady:
                    s.send(myReady.encode())
                else:
                    time.sleep(0.1)
            

            if not ready:
                ready = self.checkReady(s)

        

        self.start = data

        print("Main game loop has started")
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
        if self.lockedIn == True:
            return

        try:
            ready = s.recv(32768) # This is taking the start call and ruining everything

            if ready:
                ready = ready.decode()
                print("ready", ready)
                if ready == "p1": self.ready1 = True
                elif ready == "p2" : self.ready2 = True
                return True
        except:
            print("The other player has not readyed yet.")
            return False