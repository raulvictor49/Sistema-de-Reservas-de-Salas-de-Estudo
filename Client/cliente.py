import socket

# Configurações do Servidor
serverName = '127.0.0.1' # 127.0.0.1 é o localhost (para conversar com o Docker)
serverPort = 5000

# Cria o socket UDP do cliente
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("========================================")
print("      SISTEMA DE RESERVAS DE SALAS      ")
print("========================================")
print("Comandos disponiveis:")
print(" 1. CHECK|data (ex: CHECK|26/05)")
print(" 2. RESERVE|sala|data|hora (ex: RESERVE|Sala_A|26/05|14:00)")
print(" 3. CANCEL|id_da_reserva (ex: CANCEL|1)")
print(" Digite 'SAIR' para encerrar o cliente.")
print("========================================\n")

while True:
    # Lê o comando digitado pelo usuário
    mensagem = input("Digite o comando: ")
    
    if mensagem.upper() == 'SAIR':
        print("Encerrando o cliente...")
        break
        
    # Envia a mensagem convertida em bytes para o servidor
    clientSocket.sendto(mensagem.encode('utf-8'), (serverName, serverPort))
    
    try:
        # Define um tempo limite de 5 segundos. Se o servidor não responder, ele avisa o erro.
        clientSocket.settimeout(5.0)
        
        # Fica esperando a resposta do servidor
        resposta_bytes, serverAddress = clientSocket.recvfrom(2048)
        
        # Imprime a resposta na tela
        print(f">> RESPOSTA: {resposta_bytes.decode('utf-8')}\n")
        
    except socket.timeout:
        print(">> ERRO: O servidor não respondeu a tempo (Timeout). Verifique se ele está rodando.\n")

clientSocket.close()