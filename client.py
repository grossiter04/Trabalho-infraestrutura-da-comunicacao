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

def divide_into_packets(message):
    packets = [message[i:i+3] for i in range(0, len(message), 3)]
    return packets

def timeout_handler():
    print("Tempo limite excedido. Reenviando mensagem.")
    clientSocket.sendto(pickle.dumps("TIMEOUT"), (serverName, serverPort))

serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
seq_number = 0
serverName = input("Digite o endereço IP do servidor (ou 'localhost' para se conectar localmente): ")
config = input("Digite 0 para recepção individual e 1 para recepção em grupo. ")

while True:
    message = input("Digite uma frase em minúsculas: ")

    message += '\0'

    # Dividindo a mensagem em pacotes de 3 caracteres cada
    packets = divide_into_packets(message)

    if config == '0':
        for packet in packets:
            message_checksum = checksum(packet.encode())
            data_to_send = [seq_number, packet, message_checksum]
            
            timer = threading.Timer(5, timeout_handler)
            timer.start()
            
            clientSocket.sendto(pickle.dumps(data_to_send), (serverName, serverPort))

            # Recebendo mensagem ACK - reconhecimento
            ack, serverAddress = clientSocket.recvfrom(2048)
            ack_data = pickle.loads(ack)

            checksum_received = ack_data[2]
            print("Checksum recebida:", checksum_received)
            seq_number_received = ack_data[0]
            print("Número de sequência recebido:", seq_number_received)
            modifiedMessage = ack_data[1]
            print("Pacote recebido:", modifiedMessage, "\n")
        
            # Caso o ack_data não seja "ACK para o pacote enviado", reenvia o pacote
            while seq_number_received != seq_number+1:
                print(f"{ack_data} recebido.")
                print("ACK não recebido. Reenviando pacote.\n")
                clientSocket.sendto(pickle.dumps(data_to_send), (serverName, serverPort))
                ack, serverAddress = clientSocket.recvfrom(2048)
                ack_data = pickle.loads(ack)
                checksum_received = ack_data[2]
                print("Checksum recebida:", checksum_received)
                seq_number_received = ack_data[0]
                print("Número de sequência recebido:", seq_number_received)
                modifiedMessage = ack_data[1]
                print("Pacote recebido:", modifiedMessage, "\n")
            if seq_number_received == seq_number+1:

                print(f"{ack_data} recebido.")
                # [0, 'GAB', 202]

            timer.cancel()
                        
            if seq_number_received == seq_number+1:
                if modifiedMessage != "ERROR":
                    seq_number += 1
            else:
                print("Erro na soma de verificação ou número de sequência. Pacote ignorado.")
            time.sleep(1)
            
    elif config == '1':
        for packet in packets:
            message_checksum = checksum(packet.encode())
            data_to_send = [seq_number, packet, message_checksum]
            clientSocket.sendto(pickle.dumps(data_to_send), (serverName, serverPort))
            seq_number += 1
                
        while True:
            ack, server_address = clientSocket.recvfrom(2048)
            ack_data = pickle.loads(ack)
            print(f"ACK recebido: {ack_data}")
            # ACK x (pacote x recebido)
            print("seq_number:", seq_number)

            seq_number_received = ack_data[0]
            if seq_number_received == seq_number:
                print(f"ACK para pacote {seq_number} recebido.")
                break
            # ACK x (pacote x não recebido)
            else:
                # Dividindo "ACK x" para pegar o número do pacote
                # response DATA = [2, 'L\x00', 76]
                ack_number = int(ack_data[0])
                print(f"ACK para pacote {ack_number} não recebido. Reenviando pacote.")
                data_to_send = [int(ack_number), packets[int(ack_number)], checksum(packets[int(ack_number)].encode())]
                clientSocket.sendto(pickle.dumps(data_to_send), (serverName, serverPort))
