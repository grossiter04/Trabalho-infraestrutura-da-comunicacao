
from socket import *
import pickle
import time
import threading

def checksum(data):
    data_bytes = [bytes(element, 'utf-8') if isinstance(element, str) else bytes([element]) for element in data]
    result = 0
    for byte_data in data_bytes:
        result += int.from_bytes(byte_data, byteorder='big')
    return result & 0xFFFFFFFF

def timeout_handler():
    print("Tempo limite excedido. Reenviando mensagem.")
    clientSocket.sendto(pickle.dumps("TIMEOUT"), (serverName, serverPort))

serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
seq_number = 0
serverName = input("Digite o endereço IP do servidor (ou 'localhost' para se conectar localmente): ")

while True:
    message = input("Digite uma frase em minúsculas: ")
    if not message:
        break
    
    message_checksum = checksum(message.encode())
    data_to_send = [seq_number, message, message_checksum]
    
    timer = threading.Timer(5, timeout_handler)
    timer.start()
    
    clientSocket.sendto(pickle.dumps(data_to_send), (serverName, serverPort))

    # Recebendo mensagem ACK - reconhecimento
    ack, serverAddress = clientSocket.recvfrom(2048)
    ackk = pickle.loads(ack)
  
    while ackk != "ACK":
        print("ACK não recebido. Reenviando mensagem.\n")
        clientSocket.sendto(pickle.dumps(data_to_send), (serverName, serverPort))
        ack, serverAddress = clientSocket.recvfrom(2048)
        ackk = pickle.loads(ack)
    if ackk == "ACK":
        print(f"{ackk} recebido.")

    response_data, serverAddress = clientSocket.recvfrom(2048)

    timer.cancel()
    
    seq_number_received, modifiedMessage, checksum_received = pickle.loads(response_data)
    
    if seq_number_received == seq_number:
        print("Checksum recebida:", checksum_received)
        print("Checksum calculada:", checksum(modifiedMessage.encode()))
        print("Mensagem recebida:", modifiedMessage, "\n")
        
        if modifiedMessage != "ERROR":
            seq_number += 1
    else:
        print("Erro na soma de verificação ou número de sequência. Mensagem ignorada.")
    
    time.sleep(1)