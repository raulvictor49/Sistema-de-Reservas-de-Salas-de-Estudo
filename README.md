# Sistema de Reservas de Salas de Estudo (Socket UDP)

Este é um projeto acadêmico de um sistema cliente-servidor desenvolvido em Python, utilizando comunicação via Socket UDP. O objetivo é gerenciar a ocupação de espaços (salas de estudo) em uma universidade, garantindo persistência de dados e controle de concorrência.

## Tecnologias Utilizadas

* **Backend/Servidor:** Python (Socket UDP, `threading.Lock`)
* **Frontend/Cliente:** Python
* **Banco de Dados:** PostgreSQL
* **Infraestrutura:** Docker e Docker Compose

## Arquitetura e Funcionalidades

* **Comunicação UDP:** O cliente e o servidor se comunicam trocando datagramas via protocolo UDP na porta 5000.
* **Controle de Concorrência (Travas):** O servidor utiliza múltiplas threads para processar as mensagens recebidas. O uso de `threading.Lock` garante que dois clientes não consigam reservar a mesma sala simultaneamente.
* **Persistência em Memória e Banco de Dados:** Ao iniciar, o servidor carrega o estado atual das reservas do PostgreSQL para a memória local (cache). Novas reservas atualizam tanto o banco de dados quanto a memória, garantindo performance e persistência.

## Como Executar o Projeto

### Pré-requisitos
* Ter o **Docker** e o **Docker Compose** instalados na sua máquina.
* Ter o **Python 3** instalado na sua máquina (para executar o cliente).

### Passo 1: Iniciar a Infraestrutura (Servidor e Banco de Dados)
Abra o terminal na pasta raiz do projeto e execute o comando abaixo para construir a imagem do servidor e subir os containers do backend e do banco de dados:

```bash
docker-compose up -d --build
```

### Passo 2: Iniciar o Cliente
Abra uma nova janela de terminal, também na pasta raiz do projeto, e execute o script do cliente:

```bash
python client/cliente.py
```
## Comandos Suportados
O sistema opera através de comandos textuais enviados pelo cliente. Utilize o seguinte formato:

**Consultar Salas:** Retorna as salas ocupadas em uma determinada data.
- **Formato:** CHECK|data
- **Exemplo:** CHECK|26/05

**Reservar Sala:** Tenta reservar uma sala. Retorna sucesso (com o ID da reserva) ou falha (se já estiver ocupada).
- **Formato:** RESERVE|sala|data|hora
- **Exemplo:** RESERVE|Sala_A|26/05|14:00

**Cancelar Reserva:** Cancela uma reserva existente através do seu ID.
- **Formato:** CANCEL|id_da_reserva
- **Exemplo:** CANCEL|1
