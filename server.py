from socket import *
import hashlib
import pickle
from random import random

def checksum(data):
    # Converter todas as strings em bytes antes de calcular a soma
    data_bytes = [bytes(element, 'utf-8') if isinstance(element, str) else bytes([element]) for element in data]
    # Somar os bytes usando operadores binários
    result = 0
    for byte_data in data_bytes:
        result += int.from_bytes(byte_data, byteorder='big')
    return result & 0xFFFFFFFF


serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.bind(('', serverPort))

print("The server is ready to receive!\n")

while True:
    
    packet, clientAddress = serverSocket.recvfrom(2048)
    print("Received packet:", packet)
    print("From:", clientAddress, "\n")

    received_data = pickle.loads(packet)
    print("Received data:", received_data)

    print("Checksum calculada:", checksum(received_data[:-1][-1]))
    
    print("Checksum esperada:", received_data[-1])
    
    if checksum(received_data[:-1][-1]) == received_data[-1]:
        received_message = received_data[0]

        modifiedMessage = received_message.upper()
        response_data = [modifiedMessage, checksum([modifiedMessage])]
        serverSocket.sendto(pickle.dumps(response_data), clientAddress)

        print("Message sent to", clientAddress)
        print("Message:", modifiedMessage, "\n")
    else:
        print("Erro na soma de verificação. Requisitando reenvio...")
        errorMessage = "ERROR"
        response_data = [errorMessage, checksum([errorMessage])]
        serverSocket.sendto(pickle.dumps(response_data), clientAddress)
        print("Message sent to", clientAddress)
        print("Message:", errorMessage, "\n")
