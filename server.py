from socket import *
import pickle
import threading


# Requisitos que faltam:
# - cliente deve ser capaz de se conectar ao servidor via IP
# - Reconhecimento - falta terminar
# - Reconhecimento negativo
# - Janela, paralelismo
# - simular melhor os erros e perdas
# - Deve ser possível enviar pacotes da camada de aplicação isolados a partir do
#    cliente ou lotes com destino ao servidor. O servidor poderá ser configurado para
#    confirmar a recepção individual dessas mensagens ou em grupo (i.e. deve
#    aceitar as duas configurações);
# - Relatorio + manual de uso
# - todos os grupos que implementarem algum método de
#    checagem de integridade receberão 0,5 pontos adicionais na prova.

expected_seq_number = 0

# checa a proria integridade da mensagem
def checksum(data): 
    data_bytes = [bytes(element, 'utf-8') if isinstance(element, str) else bytes([element]) for element in data]
    result = 0
    for byte_data in data_bytes:
        result += int.from_bytes(byte_data, byteorder='big')
    return result & 0xFFFFFFFF

def timeout_handler():
    print("Tempo limite excedido. Encerrando conexão.")
    serverSocket.close()

def handle_client(packet):
    global expected_seq_number
    received_data = pickle.loads(packet)
    seq_number, received_message, received_checksum = received_data

    print(f"Sequência esperada: {expected_seq_number}, Sequência recebida: {seq_number}\n")
    
    if seq_number != expected_seq_number or checksum(received_message.encode()) != received_checksum:
        # Erro de sequência ou checksum
        return False

    expected_seq_number += 1  # Atualiza o número de sequência esperado para o próximo pacote
    return received_message.upper()  # Retorna a mensagem modificada em caso de sucesso

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print("O servidor está pronto para receber!\n")

while True:
    packet, clientAddress = serverSocket.recvfrom(2048)
    
    print("Pacote recebido:", packet)
    print("De:", clientAddress, "\n")

    timer = threading.Timer(5, timeout_handler)
    timer.start()
    
    response = handle_client(packet)
    
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

    print("Dados recebidos:", response_data, '\n')

    print("Checksum calculada:", response_data[-1])
    print("Checksum esperada:", response_data[-1], '\n')

    if ack == "ACK":        # Em seguida, enviar os dados de resposta
        serverSocket.sendto(pickle.dumps(response_data), clientAddress)
    
    print(f"{ack} enviado para {clientAddress}")
    
    timer.cancel()