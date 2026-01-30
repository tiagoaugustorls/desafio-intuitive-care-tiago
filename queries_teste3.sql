-- ==========================================================
-- TESTE 3: BANCO DE DADOS E ANÁLISE
-- Compatibilidade: MySQL 8.0+
-- ==========================================================

CREATE DATABASE IF NOT EXISTS intuitive_care_test;
USE intuitive_care_test;

-- ----------------------------------------------------------
-- 1. DDL (Estrutura das Tabelas)
-- ----------------------------------------------------------

-- Tabela Dimensão: Operadoras (Dados Cadastrais)
CREATE TABLE IF NOT EXISTS operadoras (
    registro_ans INT PRIMARY KEY,
    cnpj VARCHAR(20),
    razao_social VARCHAR(255),
    modalidade VARCHAR(100),
    uf CHAR(2),
    INDEX idx_uf (uf)
);

-- Tabela Fato: Demonstrações Contábeis (Consolidado Despesas)
CREATE TABLE IF NOT EXISTS demonstracoes_contabeis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    registro_ans INT,
    ano INT,
    trimestre CHAR(2),
    data_referencia DATE, -- Campo calculado para facilitar ordenação temporal
    valor_despesa DECIMAL(18, 2),
    descricao VARCHAR(255),
    
    FOREIGN KEY (registro_ans) REFERENCES operadoras(registro_ans),
    INDEX idx_data (data_referencia),
    INDEX idx_valor (valor_despesa)
);

-- Tabela Agregada (Opcional, pois podemos calcular via query, mas pedido no teste)
CREATE TABLE IF NOT EXISTS despesas_agregadas (
    razao_social VARCHAR(255),
    uf CHAR(2),
    valor_total DECIMAL(18, 2),
    media_trimestral DECIMAL(18, 2),
    desvio_padrao DECIMAL(18, 2),
    qtd_registros INT
);

-- ----------------------------------------------------------
-- 2. IMPORTAÇÃO DE DADOS (LOAD DATA)
-- Nota: Pode exigir configuração de 'secure-file-priv' no MySQL.
-- Ajuste os caminhos dos arquivos conforme sua máquina local.
-- ----------------------------------------------------------

-- Importando Cadastro (Relatorio_cadop.csv)
-- Tratamento: Ignora cabeçalho, trata separador ';' e converte colunas
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Relatorio_cadop.csv'
INTO TABLE operadoras
CHARACTER SET latin1
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(@registro, @cnpj, @razao, @fantasia, @modalidade, @logradouro, @num, @comp, @bairro, @cidade, @uf, @cep, @ddd, @tel, @fax, @email, @rep, @cargo, @regiao, @data_reg)
SET 
    registro_ans = CAST(@registro AS UNSIGNED),
    cnpj = @cnpj,
    razao_social = @razao,
    modalidade = @modalidade,
    uf = @uf;

-- Importando Despesas (consolidado_despesas.csv)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/consolidado_despesas.csv'
INTO TABLE demonstracoes_contabeis
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@reg_ans, @cnpj_dummy, @razao_dummy, @uf_dummy, @ano, @trimestre, @valor, @desc)
SET 
    registro_ans = CAST(@reg_ans AS UNSIGNED),
    ano = CAST(@ano AS UNSIGNED),
    trimestre = @trimestre,
    -- Transforma "1T" + "2025" em data real "2025-01-01"
    data_referencia = STR_TO_DATE(CONCAT(@ano, '-', CASE WHEN @trimestre='1T' THEN '01' WHEN @trimestre='2T' THEN '04' WHEN @trimestre='3T' THEN '07' ELSE '10' END, '-01'), '%Y-%m-%d'),
    valor_despesa = CAST(REPLACE(@valor, ',', '.') AS DECIMAL(18,2)),
    descricao = @desc;

-- ----------------------------------------------------------
-- 3. QUERIES ANALÍTICAS
-- ----------------------------------------------------------

-- Query 1: Top 5 Operadoras com maior crescimento de despesas (1T vs 3T)
-- Lógica: (Valor_Ultimo - Valor_Primeiro) / Valor_Primeiro
WITH despesas_trimestrais AS (
    SELECT 
        o.razao_social,
        SUM(CASE WHEN d.trimestre = '1T' THEN d.valor_despesa ELSE 0 END) as despesa_t1,
        SUM(CASE WHEN d.trimestre = '3T' THEN d.valor_despesa ELSE 0 END) as despesa_t3
    FROM demonstracoes_contabeis d
    JOIN operadoras o ON d.registro_ans = o.registro_ans
    WHERE d.ano = 2025
    GROUP BY o.razao_social
)
SELECT 
    razao_social,
    despesa_t1,
    despesa_t3,
    ROUND(((despesa_t3 - despesa_t1) / despesa_t1) * 100, 2) as crescimento_percentual
FROM despesas_trimestrais
WHERE despesa_t1 > 0 -- Evita divisão por zero
ORDER BY crescimento_percentual DESC
LIMIT 5;

-- Query 2: Distribuição por UF (Top 5 totais) + Média por operadora
SELECT 
    o.uf,
    SUM(d.valor_despesa) as total_despesas_uf,
    COUNT(DISTINCT d.registro_ans) as qtd_operadoras,
    ROUND(SUM(d.valor_despesa) / COUNT(DISTINCT d.registro_ans), 2) as media_por_operadora
FROM demonstracoes_contabeis d
JOIN operadoras o ON d.registro_ans = o.registro_ans
GROUP BY o.uf
ORDER BY total_despesas_uf DESC
LIMIT 5;

-- Query 3: Operadoras com despesas acima da média geral em >= 2 trimestres
-- Lógica:
-- 1. Calcula média geral POR TRIMESTRE (CTE 'medias_gerais')
-- 2. Compara cada operadora com essa média
-- 3. Conta quantas vezes ela estourou a média
WITH medias_gerais AS (
    SELECT 
        trimestre,
        AVG(valor_trimestral) as media_mercado
    FROM (
        SELECT registro_ans, trimestre, SUM(valor_despesa) as valor_trimestral
        FROM demonstracoes_contabeis
        GROUP BY registro_ans, trimestre
    ) sub
    GROUP BY trimestre
),
operadoras_vs_mercado AS (
    SELECT 
        d.registro_ans,
        d.trimestre,
        SUM(d.valor_despesa) as minha_despesa,
        m.media_mercado
    FROM demonstracoes_contabeis d
    JOIN medias_gerais m ON d.trimestre = m.trimestre
    GROUP BY d.registro_ans, d.trimestre, m.media_mercado
)
SELECT 
    COUNT(*) as qtd_operadoras_acima_media_recorrente
FROM (
    SELECT registro_ans
    FROM operadoras_vs_mercado
    WHERE minha_despesa > media_mercado
    GROUP BY registro_ans
    HAVING COUNT(*) >= 2 -- Pelo menos 2 trimestres acima
) final;