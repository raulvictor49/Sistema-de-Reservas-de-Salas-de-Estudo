import os
import psycopg2
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread, Lock

# 1. Configurações Iniciais do Servidor
serverPort = 5000 
serverSocket = socket(AF_INET, SOCK_DGRAM) 
# '0.0.0.0' é obrigatório no Docker para receber requisições externas
serverSocket.bind(('0.0.0.0', serverPort)) 

# 2. A Trava (Lock) e a Memória
# A trava garante que duas threads não reservem a mesma sala no mesmo milissegundo
reserva_lock = Lock()
# Memória em cache para guardar as salas ocupadas (formato: "Sala-Data-Hora")
salas_ocupadas_memoria = set()

# 3. Conexão com o Banco de Dados
def conectar_banco():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "reservas_db"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "adminpassword")
    )

# Carrega o estado inicial do banco para a memória ao ligar o servidor
def carregar_memoria():
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT sala, data_reserva, hora_reserva FROM reservas")
        para_cada_linha = cursor.fetchall()
        for sala, data, hora in para_cada_linha:
            salas_ocupadas_memoria.add(f"{sala}-{data}-{hora}")
        cursor.close()
        conn.close()
        print("[SERVIDOR] Memória sincronizada com o Banco de Dados.")
    except Exception as e:
        print(f"[ERRO DB] Falha ao conectar no banco: {e}")

# 4. A Função que cada Thread vai executar (O Roteador de Comandos)
def processar_mensagem(server_socket, mensagem_bytes, clientAddr):
    # Decodifica a mensagem que chegou como bytes para texto (string)
    mensagem = mensagem_bytes.decode('utf-8').strip()
    partes = mensagem.split('|')
    comando = partes[0].upper()

    resposta = "ERRO|Comando Invalido"

    try:
        if comando == "CHECK" and len(partes) == 2:
            data = partes[1]
            # Filtra a memória para ver o que está ocupado nesse dia
            ocupadas_no_dia = [item for item in salas_ocupadas_memoria if f"-{data}-" in item]
            resposta = f"Ocupadas em {data}: {', '.join(ocupadas_no_dia) if ocupadas_no_dia else 'Nenhuma'}"

        elif comando == "RESERVE" and len(partes) == 4:
            sala = partes[1]
            data = partes[2]
            hora = partes[3]
            chave = f"{sala}-{data}-{hora}"

            # INÍCIO DA ZONA CRÍTICA (Aciona a trava)
            with reserva_lock:
                if chave in salas_ocupadas_memoria:
                    resposta = "FALHA|Sala ja esta ocupada neste horario"
                else:
                    # Registra no Banco de Dados
                    conn = conectar_banco()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO reservas (sala, data_reserva, hora_reserva) VALUES (%s, %s, %s) RETURNING id",
                        (sala, data, hora)
                    )
                    resultado_db = cursor.fetchone()
                    # Verifica se o banco realmente retornou um ID
                    if resultado_db is not None:
                        id_reserva = resultado_db[0]
                    else:
                        id_reserva = "ID-Desconhecido" # Evita que o programa quebre

                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    # Atualiza a Memória RAM do servidor
                    salas_ocupadas_memoria.add(chave)
                    resposta = f"Reserva confirmada. ID: {id_reserva}"
            # FIM DA ZONA CRÍTICA (Libera a trava automaticamente)

        elif comando == "CANCEL" and len(partes) == 2:
            id_reserva = partes[1]
            
            with reserva_lock:
                conn = conectar_banco()
                cursor = conn.cursor()
                # Primeiro busca os dados para tirar da memória
                cursor.execute("SELECT sala, data_reserva, hora_reserva FROM reservas WHERE id = %s", (id_reserva,))
                resultado = cursor.fetchone()
                
                if resultado:
                    sala, data, hora = resultado
                    chave = f"{sala}-{data}-{hora}"
                    
                    # Deleta do banco
                    cursor.execute("DELETE FROM reservas WHERE id = %s", (id_reserva,))
                    conn.commit()
                    
                    # Tira da memória
                    if chave in salas_ocupadas_memoria:
                        salas_ocupadas_memoria.remove(chave)
                    resposta = f"Reserva {id_reserva} cancelada com sucesso"
                else:
                    resposta = "FALHA|ID de reserva nao encontrado"
                    
                cursor.close()
                conn.close()

    except Exception as e:
        resposta = f"ERRO|{str(e)}"

    # O servidor responde ao cliente usando o endereço de onde a carta veio
    server_socket.sendto(resposta.encode('utf-8'), clientAddr)
    print(f"Respondido para {clientAddr}: {resposta}")

# INÍCIO DA EXECUÇÃO DO SERVIDOR
if __name__ == "__main__":
    print(f"Ligando Servidor UDP na porta {serverPort}...")
    carregar_memoria()
    print("Servidor aguardando comandos...\n")

    # O Loop Infinito do UDP
    while True:
        # Fica travado aqui até chegar um pacote UDP (recvfrom substitui o accept)
        mensagem_bytes, clientAddr = serverSocket.recvfrom(1024) # 1024 é o tamanho do buffer
        print(f"\n[REBIDO] Mensagem de {clientAddr}")
        
        # Cria uma thread para processar a mensagem e já volta a escutar a porta imediatamente
        Thread(target=processar_mensagem, args=(serverSocket, mensagem_bytes, clientAddr)).start()