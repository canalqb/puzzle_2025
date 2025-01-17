import pg8000
import urllib.parse
import csv
import os
import time
import sys
from datetime import datetime

# URL de conexão com o banco de dados (substitua com sua URL), corrija o DATABASE_URL pelo fornecido em https://vercel.com/ "XXXXXXXXXX" é apenas um exemplo
DATABASE_URL = "postgres://neondb_owner:XXXXXXXXXX@ep-polished-unit-a4b64eos-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Função para obter o último valor processado no CSV
def obter_ultimo_valor_processado(caminho_csv):
    if os.path.exists(caminho_csv):
        with open(caminho_csv, mode='r', newline='') as file:
            leitor_csv = csv.reader(file)
            for linha in leitor_csv:
                return int(linha[0], 16)  # Retorna o último valor hexadecimal processado
    return 0  # Caso o CSV não exista ou esteja vazio

# Função para registrar o último valor processado no CSV
def registrar_ultimo_valor(caminho_csv, valor_processado):
    with open(caminho_csv, mode='w', newline='') as file:
        escritor_csv = csv.writer(file)
        escritor_csv.writerow([hex(valor_processado)])  # Escreve o último valor processado em hexadecimal

# Função para estabelecer uma nova conexão
def conectar_ao_banco():
    url = urllib.parse.urlparse(DATABASE_URL)
    return pg8000.connect(
        user=url.username, password=url.password,
        host=url.hostname, database=url.path[1:],  # Remover a primeira barra para o nome do banco
        port=5432,  # Porta padrão do PostgreSQL
        ssl_context=True  # Habilitar SSL
    )

# Função para reiniciar o script automaticamente
def reiniciar_script():
    print("Erro de rede detectado. Reiniciando o script...")
    time.sleep(3)  # Espera 3 segundos antes de reiniciar
    os.execv(sys.executable, [sys.executable] + sys.argv)  # Reinicia o script

# Função para gerar intervalos e inserir os dados na tabela
def gerar_intervalos(valor_inicial, valor_final, percentual, caminho_csv):
    num_divisoes = int(100 / percentual)
    intervalo_tamanho = (valor_final - valor_inicial) // num_divisoes
    dados_batch = []
    contador = 0
    
    # Reabrir conexão ao banco de dados
    connection = conectar_ao_banco()
    cursor = connection.cursor()

    try:
        for i in range(num_divisoes):
            inicio = valor_inicial + i * intervalo_tamanho
            fim = valor_inicial + (i + 1) * intervalo_tamanho
            
            # Para garantir que o último intervalo chegue exatamente no valor final
            if i == num_divisoes - 1:
                fim = valor_final

            # Convertendo os valores de "inicio" e "fim" para hexadecimal e em formato de texto
            inicio_texto = hex(inicio)
            fim_texto = hex(fim)
            durante = None
            bloqueada = False

            # Adicionar o registro na lista de dados a serem inseridos
            dados_batch.append((inicio_texto, fim_texto, durante, bloqueada))

            # Inserir em batch
            if len(dados_batch) >= envioacada:
                try:
                    insert_data_query = '''INSERT INTO puzzle67 (inicio, fim, durante, bloqueada) 
                                           VALUES (%s, %s, %s, %s)
                                           ON CONFLICT (inicio, fim) DO NOTHING;'''
                    cursor.executemany(insert_data_query, dados_batch)
                    connection.commit()
                    dados_batch.clear()
                    contador += envioacada
                    print(f"{contador} intervalos processados.")
                    # Registrar o último valor processado no CSV
                    registrar_ultimo_valor(caminho_csv, fim)
                except pg8000.exceptions.InterfaceError as e:
                    reiniciar_script()  # Se houver erro de rede, reinicia o script

        # Inserir qualquer dado restante que não tenha sido inserido em batch
        if dados_batch:
            try:
                insert_data_query = '''INSERT INTO puzzle67 (inicio, fim, durante, bloqueada) 
                                       VALUES (%s, %s, %s, %s)
                                       ON CONFLICT (inicio, fim) DO NOTHING;'''
                cursor.executemany(insert_data_query, dados_batch)
                connection.commit()
                # Registrar o último valor processado no CSV
                registrar_ultimo_valor(caminho_csv, fim)
            except pg8000.exceptions.InterfaceError as e:
                reiniciar_script()  # Se houver erro de rede, reinicia o script

        print("Intervalos processados com sucesso!")
    finally:
        cursor.close()
        connection.close()

# Caminho do arquivo CSV para salvar o último valor processado
caminho_csv = 'ultimo_valor_processado.csv'

# Números hexadecimais (valores de entrada)
hex_inicial = '40000000000000000'
hex_final = '7ffffffffffffffff'

# Convertendo os números hexadecimais para inteiros
valor_inicial = int(hex_inicial, 16)
valor_final = int(hex_final, 16)

# Solicitar ao usuário o percentual
percentual = float("0.0000001")
envioacada = 20  # Inserir registros em lotes de 20

# Verificar onde parar com base no CSV
ultimo_valor_processado = obter_ultimo_valor_processado(caminho_csv)

# Ajustar o valor inicial para o último processado
valor_inicial = ultimo_valor_processado

# Garantindo que o percentual está entre 0.000001% e 100%
if percentual <= 0 or percentual > 100:
    print("Por favor, insira um percentual maior que 0 e menor ou igual a 100%.")
else:
    # Gerar os intervalos e inserir os dados na tabela
    gerar_intervalos(valor_inicial, valor_final, percentual, caminho_csv)
