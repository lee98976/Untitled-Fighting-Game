import json
import socket
import threading
import time


class Client():
    def __init__(self, clientName, sendQueue, receiveQueue):
        # Create a thread that runs a socket
        self.sendQueue = sendQueue
        self.receiveQueue = receiveQueue
        self.mainThread = threading.Thread(target=self.const_update, args=(clientName, sendQueue, receiveQueue))
        self.mainThread.setDaemon(True)
        self.mainThread.start()

    def const_update(self, clientName, sendQueue, receiveQueue):
        # Create socket
        s = socket.socket()       
        port = 45273     

        while True:
            try:
                s.connect(('192.168.0.241', port)) # change the server ip
                break
            except:
                print("attempting server connection")
                time.sleep(1)

        s.settimeout(0.05)
        while True:
            while sendQueue.qsize() > 1:
                file_info = sendQueue.get() #Get the last packet
            file_info = sendQueue.get()
            if file_info:
                tempJson = json.dumps(file_info)
                tempJson = tempJson.encode("utf-8")
                try:
                    s.send(tempJson) # send json to server
                except Exception as error:
                    print("error: ", error)

            try:
                server_info = s.recv(10000) # recieve from the server
                if server_info:
                    server_info = server_info.decode("utf-8")
                    print(server_info)
                    server_info = json.loads(server_info)
                    receiveQueue.put(server_info)
            except:
                pass
        