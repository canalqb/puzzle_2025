# Fracionando Range do Puzzle 67 para inserir no Banco de dados NEON.

Este script foi desenvolvido para processar e inserir intervalos de valores em um banco de dados PostgreSQL, utilizando o serviço de banco de dados **Neon**. O objetivo do script é dividir um intervalo entre dois valores hexadecimais fornecidos, gerar registros para cada intervalo e inserir esses dados em uma tabela no banco de dados. Ele foi projetado para ser resiliente a falhas de rede e para garantir a continuidade do processamento através do armazenamento do último valor processado em um arquivo CSV.

## Funcionalidades

- **Conexão com Banco de Dados PostgreSQL (Neon)**: O script estabelece uma conexão com o banco de dados PostgreSQL utilizando o serviço Neon, que permite a persistência de grandes volumes de dados.
- **Processamento de Intervalos**: Divide o intervalo entre dois valores hexadecimais (`hex_inicial` e `hex_final`) com base em um percentual de divisão fornecido, processando os dados em lotes.
- **Inserção em Batch**: Os dados são inseridos em batches (lotes) de forma eficiente no banco de dados, otimizando o tempo de execução.
- **Persistência de Progresso**: O script mantém o registro do último valor processado em um arquivo CSV, permitindo que, em caso de interrupção, o processamento continue de onde parou.
- **Resiliência**: Em caso de erro de rede ou falha de conexão, o script é capaz de reiniciar automaticamente e retomar o processamento.

## Variáveis

### 1. **`DATABASE_URL`**
   - **Descrição**: Contém a URL de conexão com o banco de dados PostgreSQL (Neon).
   - **Exemplo**:
     ```python
     DATABASE_URL = "postgres://usuario:senha@hostname:porta/banco"
     ```
   - **Impacto**: Se alterada, afeta a conexão com o banco de dados. Modificações incorretas podem impedir o script de se conectar ao banco de dados.

### 2. **`caminho_csv`**
   - **Descrição**: Caminho do arquivo CSV onde o último valor processado será armazenado.
   - **Exemplo**:
     ```python
     caminho_csv = 'ultimo_valor_processado.csv'
     ```
   - **Impacto**: Se modificado, o script armazenará e lerá o valor processado de um local diferente. Certifique-se de que o caminho seja válido e tenha permissões de escrita.

### 3. **`hex_inicial` e `hex_final`**
   - **Descrição**: Definem o intervalo inicial e final dos valores a serem processados, em formato hexadecimal.
   - **Exemplo**:
     ```python
     hex_inicial = '40000000000000000'
     hex_final = '7ffffffffffffffff'
     ```
   - **Impacto**: Alterar esses valores modifica os limites do intervalo a ser processado. O valor de `hex_inicial` deve sempre ser menor que o valor de `hex_final`.

### 4. **`percentual`**
   - **Descrição**: Define o percentual de divisão entre o valor inicial e o valor final para gerar os intervalos.
   - **Exemplo**:
     ```python
     percentual = 0.0000001
     ```
   - **Impacto**: Modificar o percentual altera a granularidade dos intervalos. Percentuais menores geram intervalos mais finos, enquanto percentuais maiores geram intervalos mais largos. O valor deve estar entre 0 e 100.

### 5. **`envioacada`**
   - **Descrição**: Define o número de registros a serem inseridos no banco de dados em cada lote.
   - **Exemplo**:
     ```python
     envioacada = 20
     ```
   - **Impacto**: Se aumentado, o script processará mais registros de uma vez, melhorando a eficiência, mas aumentando o risco de erros de memória ou de sobrecarga no banco. Se diminuído, o processamento será mais lento, mas o risco de falhas diminui.

### 6. **`valor_inicial` e `valor_final` (calculados)**
   - **Descrição**: Esses valores são calculados a partir dos valores hexadecimais `hex_inicial` e `hex_final` convertidos para inteiros.
   - **Impacto**: Esses valores não precisam ser alterados diretamente, pois são recalculados automaticamente. Eles definem os limites reais dos intervalos a serem processados.

### 7. **`ultimo_valor_processado`**
   - **Descrição**: Armazena o último valor processado, lido do arquivo CSV.
   - **Impacto**: Modificar manualmente pode afetar onde o script começa o processamento. Se o valor estiver incorreto, o script pode processar intervalos já processados ou pular intervalos importantes.

## Recursos do Script

- **Conexão Segura com o Banco de Dados**: O script usa a URL de conexão para acessar o banco de dados PostgreSQL de maneira segura, com suporte para SSL.
- **Inserção Eficiente de Dados**: Utiliza a inserção em batch (lotes) para otimizar a velocidade de gravação no banco de dados.
- **Resiliência**: Em caso de erro de rede, o script reinicia automaticamente, continuando de onde parou.
- **Progresso Persistente**: O último valor processado é armazenado em um arquivo CSV, permitindo que o script retome a execução sem reprocessar intervalos já processados.

## Como Usar

### Passo 1: Configuração

1. **Clonar o repositório**:
    ```bash
    git clone https://github.com/seu-usuario/puzzle-67-2025-neon.git
    ```

2. **Instalar dependências**:
    - Certifique-se de ter o Python 3.6 ou superior instalado.
    - Instale as dependências necessárias:
    ```bash
    pip install pg8000
    ```

3. **Configurar a URL de Conexão com o Banco**:
    - Altere a variável `DATABASE_URL` no script com as credenciais corretas do seu banco de dados Neon.

### Passo 2: Executar o Script

1. Execute o script diretamente com o Python:
    ```bash
    python script.py
    ```

2. O script começará a processar os intervalos entre os valores `hex_inicial` e `hex_final` com base no percentual definido e armazenará o último valor processado no arquivo CSV.

## Contribuindo

Sinta-se à vontade para contribuir para este projeto. Caso queira adicionar funcionalidades, corrigir erros ou melhorar a documentação, siga estas etapas:

1. Faça um fork deste repositório.
2. Crie uma branch para sua feature (`git checkout -b feature/novos-recursos`).
3. Faça as alterações necessárias e commit (`git commit -am 'Adicionando novos recursos'`).
4. Envie as alterações para o seu repositório forkado (`git push origin feature/novos-recursos`).
5. Crie um pull request explicando as mudanças realizadas.

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

### Passo 4: Salvar e fechar o arquivo

Se você estiver usando o `nano` para editar, salve e feche o arquivo pressionando `CTRL + X`, depois `Y` para confirmar e `Enter` para salvar.

---

Esse arquivo `README.md` contém todas as informações sobre as variáveis, funcionalidades e recursos do script "Puzzle 67 2025 para Neon", além de instruções para uso e contribuição.
