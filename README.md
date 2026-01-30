
# Desafio Técnico - Intuitive Care

**Candidato:** Tiago Augusto Rodrigues Lima de Souza

**Vaga:** Estágio em Desenvolvimento / Dados

**Data:** Janeiro/2026

Este repositório contém a solução completa para o desafio técnico, abrangendo Engenharia de Dados (ETL), Análise, Banco de Dados e Desenvolvimento Full Stack (Web).

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
* **Python 3.8+** instalado.
* **Navegador Web** moderno (Chrome, Firefox, Edge).
* Não é necessário instalar banco de dados local (o projeto simula ou gera o SQL para portabilidade).

### Instalação
1.  Clone este repositório ou extraia o arquivo zip.
2.  Instale as dependências:
    ```bash
    pip install pandas requests beautifulsoup4 fastapi uvicorn
    ```
    *(Caso esteja usando ambiente virtual, ative-o antes: `.\venv\Scripts\activate` no Windows)*

### Execução Passo a Passo

#### 1. Teste 1: Web Scraping e ETL
Realiza a busca dos arquivos na ANS, baixa, processa e consolida os dados.
```bash
python main.py
```
Saída: Gera consolidado_despesas.csv e consolidado_despesas.zip.

#### 2. Teste 2: Transformação e Validação
Aplica regras de negócio, valida CNPJs, enriquece os dados e gera estatísticas.

```bash
python teste2.py
```
Saída: Gera despesas_agregadas.csv e Teste_Tiago_Rodrigues.zip.

#### 3. Teste 3: Banco de Dados
Gera o script SQL completo (DDL + INSERTs) para criação do banco.

```bash
python teste3_gerar_sql.py
```
Saída: Gera script_banco_dados.sql (pronto para importar em qualquer banco MySQL/PostgreSQL).

#### 4. Teste 4: API e Dashboard
Inicia o servidor Backend e disponibiliza o Frontend.

Inicie a API:

```bash
python -m uvicorn api:app --reload
```
Abra o arquivo index.html no seu navegador.

📂 Estrutura do Projeto
* main.py: Crawler da ANS e processamento ETL inicial.

* teste2.py: Script de validação de dados (Data Quality) e estatística.

* teste3_gerar_sql.py: Gerador de script SQL (Engenharia de Dados).

* api.py: Servidor Backend (FastAPI).

* index.html: Dashboard Frontend (Vue.js + Tailwind).

* script_banco_dados.sql: Dump do banco de dados gerado.

* consolidado_despesas.csv: Base de dados processada (Fato).

* Relatorio_cadop.csv: Dados cadastrais das operadoras (Dimensão).

🧠 Documentação de Decisões Técnicas (Trade-offs)
1. Processamento de Dados (ETL)
Estratégia: Processamento Incremental com Consolidação em Memória.

Decisão: Os arquivos CSV da ANS são baixados e processados um a um. Apenas as linhas filtradas ("Eventos/Sinistros") são mantidas em memória; o restante é descartado imediatamente.

Justificativa: Carregar todos os arquivos brutos simultaneamente consumiria gigabytes de RAM, causando travamento (Memory Overhead). A abordagem incremental garante escalabilidade, permitindo a execução em máquinas com recursos limitados.

2. Validação e Qualidade de Dados
Tratamento de CNPJs Inválidos:

Decisão: Validação rigorosa via cálculo de dígitos verificadores (Módulo 11). Registros inválidos são logados e excluídos das agregações estatísticas.

Justificativa: Para garantir a integridade de métricas financeiras (Média/Desvio Padrão), dados corrompidos ("lixo") não devem distorcer o cálculo.

Estratégia de Enriquecimento (Join):

Decisão: Left Join utilizando a tabela de Despesas como fato principal.

Justificativa: A prioridade é reportar a despesa financeira contábil. Caso uma operadora não seja encontrada no cadastro ativo (por inconsistência ou desativação recente), o dado financeiro é mantido com identificação "N/A" para evitar perda de informação contábil (furo de caixa).

3. Banco de Dados
Modelagem:

Decisão: Modelo Relacional Normalizado (Star Schema simplificado).

Tabela Fato: demonstracoes_contabeis (Transações).

Tabela Dimensão: operadoras (Cadastros).

Justificativa: Reduz redundância. Dados cadastrais (Razão Social, Endereço) repetidos milhões de vezes na tabela de despesas desperdiçariam armazenamento e dificultariam atualizações cadastrais (anomalia de atualização).

Tipos de Dados:

Monetário: DECIMAL(18, 2) ao invés de FLOAT.

Por que: Sistemas financeiros exigem precisão exata. FLOAT utiliza ponto flutuante binário que gera erros de arredondamento em somas grandes.

Datas: DATE.

Por que: Permite uso de funções temporais nativas do SQL (DATEDIFF, ordenação cronológica), superior ao armazenamento como texto (VARCHAR).

Estratégia de Importação (Loading):

Decisão: Geração de script SQL (INSERT INTO) via Python.

Justificativa: O comando nativo LOAD DATA INFILE do MySQL frequentemente falha por permissões de segurança (secure-file-priv) em ambientes locais Windows. O script Python garante que o avaliador possa executar o SQL gerado em qualquer cliente (DBeaver, Workbench) sem configurações complexas de servidor.

4. API e Interface Web
Framework Backend:

Decisão: FastAPI.

Justificativa: Superior ao Flask em performance (ASGI/Assíncrono) e produtividade, pois gera a documentação (Swagger UI) automaticamente e valida tipos de dados nativamente com Pydantic.

Estratégia de Paginação:

Decisão: Offset-based (page e limit).

Justificativa: O volume de dados (~20 mil registros) é estático e pequeno o suficiente para que o custo computacional do OFFSET seja irrelevante. Cursor-based adicionaria complexidade desnecessária para um dataset que não recebe inserções em tempo real durante a leitura.

Gerenciamento de Estado (Frontend):

Decisão: Vue 3 Composition API (ref/reactive).

Justificativa: A aplicação possui escopo focado (Dashboard + Modal). Utilizar bibliotecas complexas como Vuex ou Pinia adicionaria "boilerplate" desnecessário. A reatividade nativa do Vue 3 torna o código mais limpo e legível.

Busca e Filtros:

Decisão: Busca no Servidor (Server-side).

Justificativa: Enviar todos os registros para o navegador do cliente (Client-side search) causaria lentidão no carregamento inicial. A busca no servidor é mais escalável e economiza dados/memória do usuário.

📞 Contato
Email: [tiagoaugustorls@gmail.com] LinkedIn: [https://www.linkedin.com/in/tiagoaugustorls]