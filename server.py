from socket import *
import pickle
import threading

expected_seq_number = 0
first_time = True
second_time = True

# Checa a própria integridade da mensagem
def checksum(data): 
    global first_time
    data_bytes = [bytes(element, 'utf-8') if isinstance(element, str) else bytes([element]) for element in data]
    result = 0
    # Simulando um erro no checksum, alterando o primeiro byte
    if first_time:
        data_bytes[0] = bytes([data_bytes[0][0] + 1])
        first_time = False
    for byte_data in data_bytes:
        result += int.from_bytes(byte_data, byteorder='big')
    return result & 0xFFFFFFFF

def timeout_handler(client_address):
    print("Tempo limite excedido. Reenviando mensagem.")
    serverSocket.sendto(pickle.dumps("TIMEOUT"), client_address)

def handle_client(packet, client_address):
    global expected_seq_number
    global second_time
    received_data = pickle.loads(packet)
    seq_number, received_message, received_checksum = received_data

    # Simulando numero de sequencia incorreto
    if (second_time) and (first_time == False):
        seq_number = seq_number + 1
        second_time = False

    calculated_checksum = checksum(received_message.encode())

    print(f"Sequência esperada: {expected_seq_number}, Sequência recebida: {seq_number}\n")
    print(f"Checksum esperado: {received_checksum}, Checksum recebido: {calculated_checksum}\n")
    
    if seq_number != expected_seq_number:
        # Erro de sequência ou checksum
        print("Erro de sequência. Enviando NACK.\n")
        return False
    
    if(calculated_checksum != received_checksum):
        print("Erro na soma de verificação. Enviando NACK.\n")
        return False

    expected_seq_number += 1  # Atualiza o número de sequência esperado para o próximo pacote
    return received_message.upper()  # Retorna a mensagem modificada em caso de sucesso

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('0.0.0.0', serverPort))
print("O servidor está pronto para receber!\n")

# lista de mensagens recebidas onde cada indíce é uma string de pacote
received_messages = []
last_sequence_number = 0

config = input("Digite 0 para recepção individual e 1 para recepção em grupo. ")

if config == '0':
    while True:
        packet, clientAddress = serverSocket.recvfrom(2048)
        print("Pacote recebido:", pickle.loads(packet), "de ", clientAddress)

        timer = threading.Timer(5, timeout_handler, args=[clientAddress])
        timer.start()
        
        response = handle_client(packet, clientAddress)
        
        if response:
            # Envio de ACK positivo + mensagem modificada
            response_data = [expected_seq_number, response, checksum(response.encode())]
            received_messages.append(response)
            ack = "ACK " + str(expected_seq_number)
            print("Dados enviados:", response_data, '\n')
        else:
            # Envio de NACK em caso de erro
            response_data = [expected_seq_number, "ERROR", 0]
            ack = f"ACK {expected_seq_number}"

        message = ''

        # se o último caracter recebido for um '/0', a mensagem está completa
        if response != False and '\0' in response:
            print("Último pacote recebido. Mensagem completa.\n")

            # zerando a variável message para receber a próxima mensagem
            message = ''

            print("Percorrendo pacotes para montar a mensagem completa.\n")
            for i in range(last_sequence_number, expected_seq_number):
                print('Sequence number:', i)
                message += received_messages[i]
                last_sequence_number += 1
            print("Mensagem completa:", message)

        message = ''

        if ack.startswith("ACK") and config == '0':
            serverSocket.sendto(pickle.dumps(response_data), clientAddress)
            print(f"{ack} enviado para {clientAddress}\n")
            print("-"*50, '\n')

        if ack.startswith("ACK") and config == '1':
            if (response and '\0' in response) or response == False:
                serverSocket.sendto(pickle.dumps(response_data), clientAddress)
                print("Dados enviados:", response_data, '\n')
                print(f"{ack} enviado para {clientAddress}")
                
        timer.cancel()
else:
    while True:
        group_packets = {}
        final_received = False
        last_seq_number = 0
        expected_seq_number = 0
        current_seq = 0
        number_of_packets = 0
        last_sequence_number = 0
        received_messages = []
        recorrected = False

        while not final_received:
            packet, clientAddress = serverSocket.recvfrom(2048)
            received_data = pickle.loads(packet)
            seq_number, received_message, _ = received_data
            print("Pacote recebido de sequência:", seq_number)

            # Checa se é o último pacote
            if received_message and '\0' in received_message:
                final_received = True
                last_seq_number = seq_number
                print("Último pacote recebido.")
            
            print("-"*50, '\n')

            # Armazena o pacote no dicionário usando o número de sequência como chave
            group_packets[seq_number] = (packet, clientAddress)
            if(received_message != 'ERROR'):
                number_of_packets += 1

        # Processa todos os pacotes em ordem de sequência esperada
        while current_seq <= last_seq_number:
            if current_seq in group_packets:
                packet, addr = group_packets[current_seq]

                response = handle_client(packet, addr)
            
                if response:
                    # Envio de ACK positivo + mensagem modificada
                    response_data = [expected_seq_number, response, checksum(response.encode())]
                    received_messages.append(response)
                    ack = "ACK " + str(expected_seq_number)
                else:
                    # Envio de NACK em caso de erro
                    response_data = [expected_seq_number, "ERROR", 0]
                    ack = f"ACK {expected_seq_number}"

                print("Mensagem recebida:", response, "\n")

                message = ''

                # se o último caracter recebido for um '/0', a mensagem está completa
                if response != False and '\0' in response and current_seq == last_seq_number:
                    print("Último pacote recebido. Mensagem completa.\n")

                    # zerando a variável message para receber a próxima mensagem
                    message = ''

                    print("Mensagens recebidas:", received_messages, '\n')
                    print("Último número de sequência:", last_sequence_number)
                    print("Número de sequência esperado:", expected_seq_number)

                    for i in range(last_sequence_number, expected_seq_number):
                        print('Last sequence number:', i)
                        message += received_messages[i]
                        last_sequence_number += 1
                    print("Mensagem completa:", message)

                message = ''

                if ack.startswith("ACK") and config == '1':
                    if response == False:
                        while True:
                            serverSocket.sendto(pickle.dumps(response_data), clientAddress)
                            print("Dados enviados:", response_data, '\n')
                            print(f"{ack} enviado para {clientAddress}")
                            retry_packet, retry_addr = serverSocket.recvfrom(2048)
                            retry_data = pickle.loads(retry_packet)
                            retry_seq_number, _, _ = retry_data
                            print('Pacote recebido:', retry_data)
                            if retry_seq_number == expected_seq_number:
                                print(f"Pacote {current_seq} retransmitido.")
                                group_packets[current_seq] = (retry_packet, retry_addr)
                                recorrected = True
                                break
            if recorrected:
                recorrected = False
                continue
            current_seq += 1

        # Se todos os pacotes foram processados corretamente até o final
        if current_seq > last_seq_number:
            print("Todos os pacotes foram processados corretamente. Enviando ACK final.")
            print("Pacote enviado:", [current_seq, "ACK", 0])
            serverSocket.sendto(pickle.dumps([current_seq, "ACK", 0]), addr)

