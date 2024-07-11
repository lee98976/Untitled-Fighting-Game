import json
import queue
import socket
import threading
import time

class Server():
    def __init__(self):
        self.dataQueue = queue.Queue(maxsize=2) # Sends
        self.pending = queue.Queue(maxsize=2) # Sends
        self.mainThread = threading.Thread(target=self.const_update, args=(self.dataQueue, self.pending,))
        self.mainThread.daemon = True
        self.clients = []
        self.mainThread.start()
        

    def const_update(self, dataQueue, pending):
        HOST = ''  # Available to all platforms
        PORT = 45273 # Port to listen on (non-privileged ports are > 1023)
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            sleep_counter = 3
            while True:
                try:
                    s.bind((HOST, PORT))
                    s.listen()
                    break
                except:
                    print("server waiting on port opening")
                    time.sleep(sleep_counter)
                    sleep_counter *= 2

            print(f"Server listening on {HOST}:{PORT}")

            
            while True:
                conn, addr = s.accept()
                current_thread = threading.Thread(target=self.handleClient, args=(conn, addr, dataQueue, pending))
                current_thread.start()
                self.clients.append(current_thread)

            

    def handleClient(self, conn, addr, dataQueue, pending):
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(10000)


                if not pending.empty():
                    cool = pending.get()
                    conn.send(cool.encode())

                if data:
                    data = json.loads(data.decode())
                    dataQueue.put(data)
                    # print(list(dataQueue.queue))
                    if dataQueue.qsize() == 2:
                        
                        temp = dataQueue.get() # Old
                        temp2 = dataQueue.get() # New
                        returnItem = {}
                        
                        
                        if temp["owner"] == "Player1" and temp2["owner"] == "Player2":
                            returnItem["player1"] = temp["player1"]
                            returnItem["player2"] = temp2["player2"]
                        elif temp["owner"] == "Player2" and temp2["owner"] == "Player1":
                            returnItem["player2"] = temp["player2"]
                            returnItem["player1"] = temp2["player1"]
                        else:
                            # dataQueue.put(temp2)
                            #Erase everything if one client sends two packets instead of one
                            returnItem = {
                                "continue" : True,
                                "skeppy" : False
                            }
                            returnItem = json.dumps(returnItem)
                            pending.put(returnItem)
                            conn.send(returnItem.encode())
                            continue
                        
                        validAttacks = list()
                        foundIDs = set()
                        for i in temp["attacks"]:
                            if i["attackID"] not in foundIDs:
                                foundIDs.add(i["attackID"])
                                validAttacks.append(i)
                        for i in temp2["attacks"]:
                            if i["attackID"] not in foundIDs:
                                foundIDs.add(i["attackID"])
                                validAttacks.append(i)
                        returnItem["attacks"] = validAttacks

                        print(validAttacks)

                        returnItem = json.dumps(returnItem)
                        pending.put(returnItem)
                        conn.send(returnItem.encode())




                    # print("okay" , queue.qsize())
                        
                    
                # print(type(json_data))



                # print('Data type:', type(repr(data))) # repr turns the bytes into a string
                # conn.sendall(b'Data received') # send information to client
                
                # If new queue contains information, sent it to th client
                # if not que.empty():
                #    conn.send(both player dictionaries )


server = Server()
while True:
    time.sleep(0.5)