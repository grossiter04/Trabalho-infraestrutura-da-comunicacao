from socket import *
import hashlib

serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.bind(('', serverPort))

print("The server is ready to receive!\n")

while True:
    
    packet, clientAddress = serverSocket.recvfrom(2048)
    print("Received packet:", packet.decode())
    print("From:", clientAddress, "\n")
    
    # print(packet)

    received_message = packet.decode()

    modifiedMessage = received_message.upper()

    serverSocket.sendto(modifiedMessage.encode(), clientAddress)

    print("Message sent to", clientAddress)
    print("Message:", modifiedMessage, "\n")