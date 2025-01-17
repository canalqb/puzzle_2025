import pg8000
import urllib.parse
import os
import time
import gc
import sys

# Não altere minhas Variáveis:
hex_inicial = '40000000000000000'
hex_final = '7ffffffffffffffff'
percentual = float("0.0000001")
valor_inicial = int(hex_inicial, 16)
valor_final = int(hex_final, 16)
DATABASE_URL = "postgres://neondb_owner:XXXXXXXXXX@ep-polished-unit-a4b64eos-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require" 
arquivo_progresso = 'progresso.txt'
envioacada = 100  # Descrição: Define o número de registros a serem inseridos no banco de dados em cada lote.

# Função para reiniciar o script automaticamente
def reiniciar_script():
    print("Erro de rede detectado. Tentando novamente...")
    time.sleep(3)  # Espera 3 segundos antes de reiniciar
    os.execv(sys.executable, [sys.executable] + sys.argv)  # Reinicia o script

# Função para estabelecer uma nova conexão
def conectar_ao_banco():
    try:
        url = urllib.parse.urlparse(DATABASE_URL)
        return pg8000.connect(
            user=url.username, password=url.password,
            host=url.hostname, database=url.path[1:],  # Remover a primeira barra para o nome do banco
            port=5432,  # Porta padrão do PostgreSQL
            ssl_context=True  # Habilitar SSL
        )
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise

# Função para verificar se a tabela existe, e criar caso não exista
def verificar_tabela():
    connection = conectar_ao_banco()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT to_regclass('public.puzzle67');")
        result = cursor.fetchone()
        if result[0] is None:
            print("Tabela 'puzzle67' não existe. Criando agora...")
            criar_tabela()  # Cria a tabela se não existir
        else:
            print("Tabela 'puzzle67' já existe.")
    except Exception as e:
        print(f"Erro ao verificar a tabela: {e}")
    finally:
        cursor.close()
        connection.close()

# Função para criar a tabela no banco de dados
def criar_tabela():
    connection = conectar_ao_banco()
    cursor = connection.cursor() 
    try:
        # Criar a tabela se não existir
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS puzzle67 (
            inicio TEXT PRIMARY KEY,
            fim TEXT,
            durante TEXT,
            bloqueada BOOLEAN
        );
        '''
        cursor.execute(create_table_query)

        # Adicionar a restrição de unicidade para as colunas 'inicio' e 'fim'
        add_unique_constraint_query = '''
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'unique_inicio_fim') THEN
                ALTER TABLE puzzle67 ADD CONSTRAINT unique_inicio_fim UNIQUE (inicio, fim);
            END IF;
        END $$;
        '''
        cursor.execute(add_unique_constraint_query)

        connection.commit()
        print("Tabela 'puzzle67' verificada/criada com sucesso!")
    except pg8000.exceptions.DatabaseError as e:
        print(f"Erro ao criar a tabela: {e}")
        connection.rollback()  # Fazer rollback em caso de erro
    except Exception as e:
        print(f"Erro inesperado ao criar a tabela: {e}")
        connection.rollback()  # Rollback se qualquer outro erro ocorrer
    finally:
        cursor.close()
        connection.close()

# Função para ler o último valor de inicio_intervalo salvo
def ler_ultimo_progresso():
    if os.path.exists(arquivo_progresso):
        with open(arquivo_progresso, 'r') as f:
            return int(f.read().strip(), 16)
    return valor_inicial  # Se não houver progresso salvo, começa do valor inicial

# Função para salvar o último valor de inicio_intervalo
def salvar_progresso(inicio_intervalo):
    with open(arquivo_progresso, 'w') as f:
        f.write(hex(inicio_intervalo))

def gerar_tabela(valor_inicial, valor_final, percentual): 
    num_divisoes = int(100 / percentual) 
    intervalo_tamanho = (valor_final - valor_inicial) // num_divisoes 
    contador = 0 

    # Lê o último progresso salvo
    inicio_intervalo = ler_ultimo_progresso()
    
    # Calculando o índice do intervalo a ser processado
    i = (inicio_intervalo - valor_inicial) // intervalo_tamanho
    if i < 0:
        i = 0  # Garante que o valor de i não fique negativo
    
    dados_batch = []  # Lista para acumular os dados para envio em lote
    
    for i in range(i, num_divisoes):
        inicio_intervalo = valor_inicial + i * intervalo_tamanho
        fim_intervalo = valor_inicial + (i + 1) * intervalo_tamanho
        if i == num_divisoes - 1:
            fim_intervalo = valor_final 
        total = fim_intervalo - inicio_intervalo + 1 
        print(f"Intervalo {i + 1:,.0f} de {num_divisoes:,.0f}: {hex(inicio_intervalo)} até {hex(fim_intervalo)} (inclusive) é: {total:,.0f}") 
        contador += 1 
        
        # Adiciona o intervalo atual ao batch
        dados_batch.append((hex(inicio_intervalo), hex(fim_intervalo), None, False))
        
        # Envia o batch se atingir o tamanho definido por envioacada
        if len(dados_batch) >= envioacada:
            try:
                # Conectar ao banco e inserir os dados em lote
                connection = conectar_ao_banco()
                cursor = connection.cursor()
                insert_data_query = '''INSERT INTO puzzle67 (inicio, fim, durante, bloqueada) 
                                       VALUES (%s, %s, %s, %s)
                                       ON CONFLICT (inicio, fim) DO NOTHING;'''
                cursor.executemany(insert_data_query, dados_batch)
                connection.commit()
                dados_batch.clear()  # Limpar o batch após o envio
                connection.close()

                contador += envioacada
                print(f"{contador} intervalos processados.")
                
            except pg8000.exceptions.InterfaceError as e:
                print(f"Erro ao enviar batch de dados: {e}. Reiniciando o script.")
                reiniciar_script()  # Caso ocorra um erro de conexão, reinicia o script

            # Coleta o lixo após cada envio de batch
            print("Coletando lixo após envio de batch...")
            gc.collect()

        # Salva o progresso após cada intervalo
        salvar_progresso(inicio_intervalo)

        # Coleta o lixo após um número de intervalos processados
        if contador % 1000 == 0:
            print(f"{contador} intervalos processados. Coletando lixo...")
            gc.collect()

        # time.sleep(4)  # Para não sobrecarregar a conexão com o banco

    # Envia qualquer dado restante no batch (caso o número total de registros não seja múltiplo de envioacada)
    if dados_batch:
        try:
            connection = conectar_ao_banco()
            cursor = connection.cursor()
            insert_data_query = '''INSERT INTO puzzle67 (inicio, fim, durante, bloqueada) 
                                   VALUES (%s, %s, %s, %s)
                                   ON CONFLICT (inicio, fim) DO NOTHING;'''
            cursor.executemany(insert_data_query, dados_batch)
            connection.commit()
            cursor.close()
            connection.close()
            print(f"{contador} intervalos processados.")
        except pg8000.exceptions.InterfaceError as e:
            print(f"Erro ao enviar batch final de dados: {e}. Reiniciando o script.")
            reiniciar_script()  # Caso ocorra um erro de conexão, reinicia o script

        # Coleta o lixo após o envio do último batch
        print("Coletando lixo após envio final de batch...")
        gc.collect()

# Chamada da função para verificar a tabela antes de gerar os dados
verificar_tabela()

# Chamada da função para gerar a tabela com os parâmetros corretos
gerar_tabela(valor_inicial, valor_final, percentual)
