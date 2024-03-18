from socket import *

serverName = "localhost"
serverPort = 1200

clientSocket = socket(AF_INET, SOCK_DGRAM)

message = input("Enter a lowercase sentence: ")

clientSocket.sendto(message.encode(), (serverName, serverPort))

modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage.decode())

clientSocket.close()