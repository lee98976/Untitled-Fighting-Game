import threading
import socket
import time

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
        self.servers = []

        # Start main thread that is looking for connections
        self.mainThread = threading.Thread(target=self.const_update, args=())
        self.mainThread.daemon = True
        self.mainThread.start()
    
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
                    print("Server is waiting on port opening")
                    time.sleep(sleep_counter)
                    sleep_counter *= 1.3

            print("Server has successfully found a port!")
            print(f"Listening on {HOST}:{PORT}...")
            
            while True:
                # Look for any connecting clients
                conn, addr = s.accept()
                current_thread = threading.Thread()
                self.clients.append(current_thread)
                current_thread.start()
    
    def updateAll()
