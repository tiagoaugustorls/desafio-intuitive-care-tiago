import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import math
import os

app = FastAPI(title="Intuitive Care API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURAÇÕES ---
ARQUIVO_DESPESAS = "consolidado_despesas.csv"
ARQUIVO_CADASTRO = "Relatorio_cadop.csv"

# Variáveis globais para armazenar os dados na memória
df_despesas = pd.DataFrame()
df_operadoras = pd.DataFrame()

def carregar_dados_blindado():
    """Carrega e força a tipagem correta para o JOIN funcionar."""
    print("--- INICIANDO CARGA DE DADOS ---")
    
    global df_despesas, df_operadoras
    
    # 1. Carrega Despesas
    if os.path.exists(ARQUIVO_DESPESAS):
        try:
            df_d = pd.read_csv(ARQUIVO_DESPESAS, sep=';', encoding='utf-8-sig')
            # FORÇA O REGISTRO ANS SER INTEIRO (Remove .0 se existir)
            df_d['RegistroANS'] = pd.to_numeric(df_d['RegistroANS'], errors='coerce').fillna(0).astype(int)
            print(f"-> Despesas carregadas: {len(df_d)} registros.")
        except Exception as e:
            print(f"Erro ao ler despesas: {e}")
            df_d = pd.DataFrame()
    else:
        print("ERRO: consolidado_despesas.csv não encontrado.")
        df_d = pd.DataFrame()

    # 2. Carrega Cadastro
    if os.path.exists(ARQUIVO_CADASTRO):
        try:
            # Tenta ler com ; ou ,
            try:
                df_c = pd.read_csv(ARQUIVO_CADASTRO, sep=';', encoding='utf-8', on_bad_lines='skip')
            except:
                df_c = pd.read_csv(ARQUIVO_CADASTRO, sep=';', encoding='latin1', on_bad_lines='skip')
            
            # Normaliza nomes de colunas
            df_c.columns = [c.strip().upper().replace('_', '').replace(' ', '') for c in df_c.columns]
            
            # Acha as colunas certas
            col_reg = next((c for c in df_c.columns if 'REGISTRO' in c or 'CDOP' in c), None)
            col_cnpj = next((c for c in df_c.columns if 'CNPJ' in c), 'CNPJ')
            col_razao = next((c for c in df_c.columns if 'RAZAO' in c or 'NOME' in c), 'RazaoSocial')
            col_uf = next((c for c in df_c.columns if 'UF' in c), 'UF')

            if col_reg:
                df_c = df_c.rename(columns={col_reg: 'RegistroANS', col_cnpj: 'CNPJ', col_razao: 'RazaoSocial', col_uf: 'UF'})
                # FORÇA O REGISTRO ANS SER INTEIRO AQUI TAMBÉM
                df_c['RegistroANS'] = pd.to_numeric(df_c['RegistroANS'], errors='coerce').fillna(0).astype(int)
                
                # Remove duplicatas
                df_c = df_c.drop_duplicates(subset=['RegistroANS'])
                print(f"-> Operadoras carregadas: {len(df_c)} registros.")
            else:
                print("ERRO: Coluna RegistroANS não encontrada no cadastro.")
                df_c = pd.DataFrame()
        except Exception as e:
            print(f"Erro ao ler cadastro: {e}")
            df_c = pd.DataFrame()
    else:
        print("ERRO: Relatorio_cadop.csv não encontrado.")
        df_c = pd.DataFrame()

    df_despesas = df_d
    df_operadoras = df_c

# Executa a carga ao iniciar
carregar_dados_blindado()

# --- ROTAS ---

@app.get("/api/operadoras")
def listar_operadoras(page: int = Query(1), limit: int = Query(10), search: Optional[str] = None):
    if df_operadoras.empty: return {"data": [], "meta": {"total": 0}}

    df_filt = df_operadoras.copy()
    if search:
        s = search.lower()
        df_filt = df_filt[
            df_filt['RazaoSocial'].astype(str).str.lower().str.contains(s, na=False) |
            df_filt['CNPJ'].astype(str).str.contains(s, na=False) |
            df_filt['RegistroANS'].astype(str).str.contains(s, na=False) # Busca também por Registro
        ]

    total = len(df_filt)
    start = (page - 1) * limit
    end = start + limit
    
    data = df_filt.iloc[start:end].fillna("").to_dict(orient="records")
    return {"data": data, "meta": {"total": total, "page": page, "limit": limit, "total_pages": math.ceil(total/limit)}}

@app.get("/api/operadoras/{identificador}/despesas")
def get_despesas(identificador: str):
    """Busca despesas pelo Registro ANS ou CNPJ."""
    if df_despesas.empty: return []

    # Limpa o identificador (remove pontos e traços se for CNPJ)
    id_clean = ''.join(filter(str.isdigit, str(identificador)))
    
    registro_alvo = None

    # 1. Tenta achar qual é o RegistroANS desse identificador
    # Verifica se o ID passado já é um Registro ANS válido (existe na lista de operadoras)
    try:
        id_int = int(id_clean)
        if id_int in df_operadoras['RegistroANS'].values:
            registro_alvo = id_int
    except: pass

    # Se não achou direto, procura pelo CNPJ
    if registro_alvo is None:
        op = df_operadoras[df_operadoras['CNPJ'].astype(str).str.replace(r'[^0-9]', '', regex=True) == id_clean]
        if not op.empty:
            registro_alvo = op.iloc[0]['RegistroANS']
    
    if registro_alvo is None:
        print(f"Aviso: Operadora {identificador} não encontrada.")
        return []

    # 2. Filtra as despesas usando o RegistroANS (Inteiro)
    print(f"Buscando despesas para RegistroANS: {registro_alvo}")
    filtro = df_despesas[df_despesas['RegistroANS'] == registro_alvo].copy()
    
    if filtro.empty:
        return []

    return filtro.sort_values(by=['Ano', 'Trimestre'])[['Ano', 'Trimestre', 'Valor Despesas', 'Descricao']].fillna("").to_dict(orient="records")

@app.get("/api/estatisticas")
def get_stats():
    if df_despesas.empty: return {"total_geral": 0, "top_ufs": []}
    
    total = df_despesas['Valor Despesas'].sum()
    
    # Top UFs
    # Faz join se necessário, ou usa o que tiver
    if 'UF' not in df_despesas.columns:
        df_join = pd.merge(df_despesas, df_operadoras[['RegistroANS', 'UF']], on='RegistroANS', how='left')
    else:
        df_join = df_despesas
        
    top_ufs = df_join.groupby('UF')['Valor Despesas'].sum().sort_values(ascending=False).head(5)
    grafico = [{"uf": k, "total": v} for k,v in top_ufs.items()]
    
    return {"total_geral": total, "top_ufs": grafico}