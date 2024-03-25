from socket import *
import pickle
import time

# Função para calcular a soma de verificação
def checksum(data):
    # Converter todas as strings em bytes antes de calcular a soma
    data_bytes = [bytes(element, 'utf-8') if isinstance(element, str) else bytes([element]) for element in data]
    # Somar os bytes usando operadores binários
    result = 0
    for byte_data in data_bytes:
        result += int.from_bytes(byte_data, byteorder='big')
    return result & 0xFFFFFFFF


serverName = "localhost"
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)
while True:
    message = input("Enter a lowercase sentence: ")
    
    message_checksum = checksum(message.encode())

    data_to_send = [message, 12]
    clientSocket.sendto(pickle.dumps(data_to_send), (serverName, serverPort))

    response_data, serverAddress = clientSocket.recvfrom(2048)

    # Separa a mensagem e a soma de verificação
    modifiedMessage, checksum_received = pickle.loads(response_data)

    if (modifiedMessage == "ERROR"):
        # Reenviando mensagem
        print("Erro na soma de verificação. Reenviando mensagem...")
        data_to_send = [message, message_checksum]
        clientSocket.sendto(pickle.dumps(data_to_send), (serverName, serverPort))
    else:
        print("Checksum recebida:", checksum_received)
        print("Checksum calculada:", checksum(modifiedMessage.encode()))
    

    print(modifiedMessage)

    time.sleep(1)
