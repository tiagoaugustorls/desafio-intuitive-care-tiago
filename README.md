# 🏥 Desafio Técnico - Intuitive Care

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-Compatible-4479A1?style=for-the-badge&logo=mysql&logoColor=white)

> **Candidato:** Tiago Augusto Rodrigues Lima de Souza  
> **Vaga:** Estágio em Desenvolvimento / Dados  
> **Data:** Janeiro/2026

Este repositório contém a solução completa para o desafio técnico, abrangendo **Engenharia de Dados (ETL)**, **Análise de Qualidade**, **Banco de Dados** e **Desenvolvimento Full Stack (Web)**.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
* **Python 3.8+** instalado.
* **Navegador Web** moderno (Chrome, Firefox, Edge).
* *Nota:* Não é necessário instalar banco de dados local (o projeto simula ou gera o SQL para portabilidade).

### 📦 Instalação

1. **Clone este repositório** ou extraia o arquivo `.zip`.
2. **Instale as dependências** via terminal:

```bash
pip install pandas requests beautifulsoup4 fastapi uvicorn
```
💡 Dica: Caso esteja usando um ambiente virtual (venv), ative-o antes:.
```bash
\venv\Scripts\activate (Windows)
```
ou ```bash source venv/bin/activate (Linux/Mac).```
### 👣 Execução Passo a Passo
1️⃣ Teste 1: Web Scraping e ETLRealiza a busca dos arquivos na ANS, baixa, processa e consolida os dados.Bashpython main.py 

✅ Saída: Gera consolidado_despesas.csv e consolidado_despesas.zip.

2️⃣ Teste 2: Transformação e ValidaçãoAplica regras de negócio, valida CNPJs, enriquece os dados e gera estatísticas.Bashpython teste2.py

✅ Saída: Gera despesas_agregadas.csv e Teste_Tiago_Rodrigues.zip.

3️⃣ Teste 3: Banco de DadosGera o script SQL completo (DDL + INSERTs) para criação do banco.Bashpython teste3_gerar_sql.py

✅ Saída: Gera script_banco_dados.sql (pronto para importar em qualquer banco MySQL/PostgreSQL).

4️⃣ Teste 4: API e DashboardInicia o servidor Backend e disponibiliza o Frontend.Inicie a API:Bashpython -m uvicorn api:app --reload
Acesse o Dashboard:Abra o arquivo index.html no seu navegador (basta dar um duplo clique no arquivo).
### 📂 Estrutura do Projeto

|Arquivo|Descrição|
| ------| ------|
|main.py|Crawler da ANS e processamento ETL inicial.|
|teste2.py|Script de validação de dados (Data Quality) e estatística.|
|teste3_gerar_sql.py|Gerador de script SQL (Engenharia de Dados).|
|api.py|Servidor Backend (FastAPI).|
|index.html|Dashboard Frontend (Vue.js + Tailwind).|
|script_banco_dados.sql|Dump do banco de dados gerado.|
|consolidado_despesas.csv|Base de dados processada (Fato).|
|Relatorio_cadop.csv|Dados cadastrais das operadoras (Dimensão).|

### 🧠 Documentação de Decisões Técnicas (Trade-offs)

🛠️ Processamento de Dados (ETL)
* Estratégia: Processamento Incremental com Consolidação em Memória.
* Decisão: Os arquivos CSV da ANS são baixados e processados um a um. Apenas as linhas filtradas ("Eventos/Sinistros") são mantidas em memória; o restante é descartado imediatamente.
* Justificativa: Carregar todos os arquivos brutos simultaneamente consumiria gigabytes de RAM, causando travamento (Memory Overhead). A abordagem incremental garante escalabilidade em máquinas com recursos limitados.

✅ Validação e Qualidade de Dados

* Tratamento de CNPJs Inválidos:

  * Decisão: Validação rigorosa via cálculo de dígitos verificadores (Módulo 11). Registros inválidos são logados e excluídos das agregações. 
  * Justificativa: Para garantir a integridade de métricas financeiras (Média/Desvio Padrão), dados corrompidos não devem distorcer o cálculo.
* Estratégia de Enriquecimento (Join):
  * Decisão: Left Join utilizando a tabela de Despesas como fato principal.
  * Justificativa: A prioridade é reportar a despesa financeira. Caso uma operadora não seja encontrada no cadastro ativo, o dado financeiro é mantido com identificação "N/A" para evitar perda de informação contábil ("furo de caixa").
## 🗄️ Banco de Dados
* Modelagem:
  * Decisão: Modelo Relacional Normalizado (Star Schema simplificado). Fato: ```demonstracoes_contabeis``` | Dimensão: ```operadoras```.
  * Justificativa: Reduz redundância. Dados cadastrais repetidos milhões de vezes na tabela de despesas desperdiçariam armazenamento e dificultariam atualizações.
* Tipos de Dados:
  * Monetário: ```DECIMAL(18, 2)``` (Sistemas financeiros exigem precisão exata; ```FLOAT``` gera erros de arredondamento).
  * Datas: ```DATE``` (Permite funções temporais nativas do SQL, superior a ```VARCHAR```).
* Importação (Loading):
  * Decisão: Geração de script SQL (```INSERT INTO```) via Python.
  * Justificativa: Contorna problemas de permissão (```secure-file-priv```) comuns no comando ```LOAD DATA INFILE``` em ambientes Windows locais, garantindo que o avaliador consiga executar o SQL em qualquer cliente.
## 💻 API e Interface Web
* Framework Backend:
  * Decisão: FastAPI.
  * Justificativa: Superior ao Flask em performance (ASGI) e produtividade (documentação automática Swagger e validação com Pydantic).
* Paginação:
  * Decisão: Offset-based (```page``` e ```limit```).
  * Justificativa: O volume de dados (~20 mil registros) é estático e pequeno o suficiente para que o custo do OFFSET seja irrelevante.
* Gerenciamento de Estado (Frontend):
  * Decisão: Vue 3 Composition API (```ref```/```reactive```).
  * Justificativa: Aplicação com escopo focado. Bibliotecas como Vuex/Pinia adicionariam complexidade desnecessária.
* Busca e Filtros:
  * Decisão: Busca no Servidor (Server-side).
  * Justificativa: Enviar todos os registros para o cliente (Client-side) causaria lentidão no carregamento inicial.

### 📞 Contato
Email: [tiagoaugustorls@gmail.com] LinkedIn: [https://www.linkedin.com/in/tiagoaugustorls]