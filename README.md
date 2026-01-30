# 🏥 Desafio Técnico - Intuitive Care

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-Layered-orange?style=for-the-badge)

> **Candidato:** Tiago Augusto Rodrigues Lima de Souza  
> **Vaga:** Estágio em Desenvolvimento / Dados  
> **Data:** Janeiro/2026

Este repositório contém a solução completa para o desafio técnico. O projeto foi estruturado seguindo uma **arquitetura de pipeline em camadas**, garantindo a separação clara de responsabilidades entre Dados, Banco, Backend e Frontend.

---

## 🏛️ Arquitetura da Solução

O projeto está organizado em 4 camadas sequenciais:

| Camada | Arquivo | Responsabilidade |
| :--- | :--- | :--- |
| **1. ETL (Extração)** | `1_ETL_Crawler.py` | Crawler da ANS. Baixa, processa e consolida arquivos CSV incrementalmente. |
| **2. ETL (Qualidade)** | `2_ETL_Transformacao.py` | Validação de CNPJs, enriquecimento de dados e cálculo de estatísticas. |
| **3. Banco de Dados** | `3_SQL_Database.py` | Modelagem Dimensional e geração automática de scripts SQL (DDL/DML). |
| **4. Aplicação** | `4_Backend_API.py` <br> `5_Frontend_Dashboard.html` | API REST (FastAPI) e Interface Reativa (Vue.js). |

---

## 🚀 Como Executar

### Pré-requisitos
* **Python 3.8+**

### 📦 Instalação
1. Clone o repositório.
2. Instale as dependências:

```bash
   pip install pandas requests beautifulsoup4 fastapi uvicorn
```
💡 Dica: Caso esteja usando um ambiente virtual (venv), ative-o antes:.

```bash
\venv\Scripts\activate (Windows)
```
ou 

```bash 
source venv/bin/activate (Linux/Mac).
```

### ▶️ Execução Automática (Pipeline de Dados)
Para rodar todas as etapas de dados (1, 2 e 3) de forma sequencial, execute o orquestrador:

```bash 
python run_pipeline.py
```
### 🌐 Execução da Aplicação Web
Após gerar os dados, inicie o servidor da API:

```bash 
python -m uvicorn 4_Backend_API:app --reload
```
Em seguida, abra o arquivo ```5_Frontend_Dashboard.html``` no seu navegador.

### 🧠 Decisões Técnicas (Trade-offs)

#### 1. Separação de Responsabilidades (Arquitetura)
  * Decisão: Adoção de scripts numerados sequenciais (1_..., 2_...) em vez de um único script monolítico.

  * Justificativa: Facilita a manutenção e o debug. Se o erro for no download, ajustamos apenas a camada 1 sem impactar a API. Atende ao requisito de "Separação clara entre ETL, Banco e Interface".

#### 2. Estratégia de Dados (ETL)
  * Decisão: Processamento em memória com Pandas e persistência em CSV/SQL.

  * Justificativa: Para o volume de dados do teste (~20k registros), o Pandas oferece a melhor performance sem a sobrecarga de configurar um servidor Spark ou Airflow.

#### 3. API e Frontend
  * Backend: FastAPI escolhido pela validação de dados nativa e performance assíncrona.

  * Frontend: Vue.js (CDN) utilizado para eliminar a necessidade de npm install e build, permitindo que a interface seja testada imediatamente em qualquer navegador.


### 📞 Contato
Email: [tiagoaugustorls@gmail.com] LinkedIn: [https://www.linkedin.com/in/tiagoaugustorls]