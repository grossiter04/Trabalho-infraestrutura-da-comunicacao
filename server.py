from socket import *
import pickle
import threading

# Requisitos que faltam:
# - temporizador precisa reenviar a mensagem - paixao e mega
# - Reconhecimento negativo - falta terminar - carlos e rossiter
# - Janela, paralelismo - paixa e mega
# - Deve ser possível enviar pacotes da camada de aplicação isolados a partir do
#    cliente ou lotes com destino ao servidor. O servidor poderá ser configurado para
#    confirmar a recepção individual dessas mensagens ou em grupo (i.e. deve
#    aceitar as duas configurações); - quem terminar sua parte vai ajudando aqui
# - Relatorio + manual de uso - qualquer um

expected_seq_number = 0
first_time = True

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
    received_data = pickle.loads(packet)
    seq_number, received_message, received_checksum = received_data
    calculated_checksum = checksum(received_message.encode())

    print(f"Sequência esperada: {expected_seq_number}, Sequência recebida: {seq_number}\n")
    print(f"Checksum esperado: {received_checksum}, Checksum recebido: {calculated_checksum}\n")
    
    if seq_number != expected_seq_number or calculated_checksum != received_checksum:
        # Erro de sequência ou checksum
        print("Erro na soma de verificação ou número de sequência. Enviando NACK.\n")
        return False

    expected_seq_number += 1  # Atualiza o número de sequência esperado para o próximo pacote
    return received_message.upper()  # Retorna a mensagem modificada em caso de sucesso

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('0.0.0.0', serverPort))
print("O servidor está pronto para receber!\n")

while True:
    packet, clientAddress = serverSocket.recvfrom(2048)
    print("Pacote recebido:", packet)
    print("De:", clientAddress, "\n")

    timer = threading.Timer(5, timeout_handler, args=[clientAddress])
    timer.start()
    
    response = handle_client(packet, clientAddress)
    
    if response:
        # Envio de ACK positivo + mensagem modificada
        response_data = [expected_seq_number - 1, response, checksum(response.encode())]
        ack = "ACK"
    else:
        # Envio de NACK em caso de erro
        response_data = [expected_seq_number - 1, "ERROR", 0]
        ack = "NACK"
    
    # Primeiro, enviar o ACK ou NACK
    serverSocket.sendto(pickle.dumps(ack), clientAddress)

    print("Dados enviados:", response_data, '\n')

    if ack == "ACK":  # Em seguida, enviar os dados de resposta
        serverSocket.sendto(pickle.dumps(response_data), clientAddress)
    
    print(f"{ack} enviado para {clientAddress}")
    
    timer.cancel()