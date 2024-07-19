import threading
import socket
import time
import queue
import json

from game.server.startServer import StartServer

class MatchMakingServer():
    '''
    This class is supposed to take in all clients and all available servers to show on
    the clients UI. It will connect to clients and give information on player count and
    available servers every second.
    '''

    def __init__(self):
        # A list of all clients connections
        self.clients = []

        # A list of all available gameplay servers (lobby) with PORT
        
        self.availablePorts = queue.Queue()
        self.availablePorts.put(45273)
        self.availablePorts.put(45300)
        self.availablePorts.put(45600)
        self.availablePorts.put(45614)
        self.servers = []

        # Start main thread that is looking for connections
        self.mainThread = threading.Thread(target=self.const_update, args=())
        self.mainThread.daemon = True
        self.mainThread.start()

        while True:
            time.sleep(1)
    
    def const_update(self):
        HOST = ''  # Available to all platforms
        PORT = 45200 # Port to listen to (Make sure it is available)

        # Create a socket object s
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            sleep_counter = 1
            while True:
                try:
                    s.bind((HOST, PORT))
                    s.listen()
                    break
                except:
                    print("Match making server is waiting on port opening")
                    time.sleep(sleep_counter)
                    sleep_counter *= 1.3

            print("Match making server has successfully found a port!")
            print(f"Listening on {HOST}:{PORT}...")

            self.serverThread = threading.Thread(target=self.updateServer, args=())
            self.serverThread.daemon = True
            self.serverThread.start()

            self.serverThread2 = threading.Thread(target=self.updateServer, args=())
            self.serverThread2.daemon = True
            self.serverThread2.start()
            
            while True:
                # Look for any connecting clients
                conn, addr = s.accept()
                current_thread = threading.Thread(target=self.updateClient, args=(conn, addr,))
                self.clients.append(current_thread)
                current_thread.start()
    
    def compileServers(self):
        serverAsJSON = []
        for server in self.servers:
            if server.server.player1 == False and server.server.player2 == False: numPlayers = 0
            elif server.server.player1 == True and server.server.player2 == False: numPlayers = 1
            elif server.server.player1 == True and server.server.player2 == True: numPlayers = 2
            serverAsJSON.append([server.server.PORT, numPlayers])
        serverAsJSON = json.dumps(serverAsJSON)
        return serverAsJSON

    def updateClient(self, conn, addr):
        with conn:
            username = "lee98976" # Tempelate for SQL later
            print('Connected to', addr, ", Username:", username)
            while True:
                serverAsJSON = self.compileServers()
                try: conn.send(serverAsJSON.encode())
                except: return
                time.sleep(1)
    
    def updateServer(self):
        port = self.availablePorts.get()
        print(port)
        aServer = StartServer(port, self)
        