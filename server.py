from socket import *
import pickle
import threading  # Importe a biblioteca threading

def checksum(data):
    data_bytes = [bytes(element, 'utf-8') if isinstance(element, str) else bytes([element]) for element in data]
    result = 0
    for byte_data in data_bytes:
        result += int.from_bytes(byte_data, byteorder='big')
    return result & 0xFFFFFFFF

def timeout_handler():
    print("Tempo limite excedido. Encerrando conexão.")
    serverSocket.close()

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("O servidor está pronto para receber!\n")

while True:
    packet, clientAddress = serverSocket.recvfrom(2048)
    print("Pacote recebido:", packet)
    print("De:", clientAddress, "\n")

    timer = threading.Timer(5, timeout_handler)  # Define um tempo limite de 5 segundos
    timer.start()

    received_data = pickle.loads(packet)
    print("Dados recebidos:", received_data)

    print("Checksum calculada:", checksum(received_data[:-1][-1]))
    print("Checksum esperada:", received_data[-1])

    # Pare o temporizador após receber os dados do cliente
    timer.cancel()

    if checksum(received_data[:-1][-1]) == received_data[-1]:
        received_message = received_data[0]
        modifiedMessage = received_message.upper()
        response_data = [modifiedMessage, checksum(modifiedMessage)]
        serverSocket.sendto(pickle.dumps(response_data), clientAddress)
        print("Mensagem enviada para", clientAddress)
        print("Mensagem:", modifiedMessage, "\n")
    else:
        print("Erro na soma de verificação. Requisitando reenvio...")
        errorMessage = "ERROR"
        response_data = [errorMessage, checksum(errorMessage)]
        serverSocket.sendto(pickle.dumps(response_data), clientAddress)
        print("Mensagem enviada para", clientAddress)
        print("Mensagem:", errorMessage, "\n")
