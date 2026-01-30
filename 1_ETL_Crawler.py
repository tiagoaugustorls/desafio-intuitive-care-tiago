import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import zipfile
import io
import re
import urllib3

# Desabilita avisos de segurança (sites do governo)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURAÇÕES ---
BASE_URL_CONTABIL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
URL_CADASTRO = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"
ARQUIVO_CADASTRO_LOCAL = "Relatorio_cadop.csv"

USER_AGENT = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def garantir_cadastro():
    if os.path.exists(ARQUIVO_CADASTRO_LOCAL):
        print(f"-> Arquivo de cadastro já existe: {ARQUIVO_CADASTRO_LOCAL}")
        return True
    
    print(f"-> Baixando cadastro de: {URL_CADASTRO} ...")
    try:
        r = requests.get(URL_CADASTRO, headers=USER_AGENT, verify=False, timeout=60)
        if r.status_code == 200:
            with open(ARQUIVO_CADASTRO_LOCAL, 'wb') as f:
                f.write(r.content)
            print("-> Cadastro baixado com SUCESSO!")
            return True
        else:
            print(f"-> Erro HTTP ao baixar cadastro: {r.status_code}")
    except Exception as e:
        print(f"-> Erro de conexão ao baixar cadastro: {e}")
    return False

def ler_csv_inteligente(caminho):
    separadores = [';', ',']
    encodings = ['utf-8', 'latin1', 'utf-8-sig', 'cp1252']
    
    for enc in encodings:
        for sep in separadores:
            try:
                if hasattr(caminho, 'seek'): caminho.seek(0)
                df_teste = pd.read_csv(caminho, sep=sep, encoding=enc, nrows=2, on_bad_lines='skip')
                if len(df_teste.columns) > 1:
                    if hasattr(caminho, 'seek'): caminho.seek(0)
                    print(f"   (Leitura OK: {enc} com '{sep}')")
                    return pd.read_csv(caminho, sep=sep, encoding=enc, on_bad_lines='skip')
            except: continue
            
    try:
        if hasattr(caminho, 'seek'): caminho.seek(0)
        return pd.read_csv(caminho, on_bad_lines='skip')
    except:
        return pd.DataFrame()

def listar_urls_trimestres():
    print(f"--- 1. Buscando trimestres ---")
    try:
        response = requests.get(BASE_URL_CONTABIL, headers=USER_AGENT, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        links_anos = sorted([a.get('href') for a in soup.find_all('a') 
                             if a.get('href').replace('/','').strip().isdigit()], reverse=True)
        
        urls_finais = []
        for ano in links_anos[:2]:
            url_ano = BASE_URL_CONTABIL + ano
            try:
                resp = requests.get(url_ano, headers=USER_AGENT, verify=False)
                soup_ano = BeautifulSoup(resp.text, 'html.parser')
                links = [url_ano + a.get('href') for a in soup_ano.find_all('a') 
                         if ('T' in a.get('href').upper() or '.zip' in a.get('href').lower()) and not a.get('href').startswith('?')]
                urls_finais.extend(sorted(links, reverse=True))
                if len(urls_finais) >= 3: break
            except: continue
        return urls_finais[:3]
    except: return []

def baixar_e_extrair(url, destino):
    try:
        os.makedirs(destino, exist_ok=True)
        r = requests.get(url, headers=USER_AGENT, verify=False)
        if url.endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(r.content)) as z: z.extractall(destino)
        else: 
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all('a'):
                if a.get('href').lower().endswith('.zip'):
                    full = url + a.get('href')
                    if a.get('href').startswith('http'): full = a.get('href')
                    rz = requests.get(full, headers=USER_AGENT, verify=False)
                    with zipfile.ZipFile(io.BytesIO(rz.content)) as z: z.extractall(destino)
    except Exception as e: print(f"Erro download: {e}")

def processar_despesas(diretorio):
    print("\n--- 2. Processando Despesas ---")
    dfs = []
    for root, _, files in os.walk(diretorio):
        for file in files:
            if file.lower().endswith(('.csv', '.txt')):
                try:
                    path = os.path.join(root, file)
                    df = ler_csv_inteligente(path)
                    
                    if df.empty: continue

                    col_desc = next((c for c in df.columns if 'DESC' in c.upper()), None)
                    if not col_desc: continue
                    
                    df = df[df[col_desc].str.upper().str.contains('EVENTO|SINISTRO', na=False)].copy()
                    if df.empty: continue
                    
                    df.rename(columns={'REG_ANS': 'RegistroANS', 'CD_OP': 'RegistroANS', 
                                       'CD_CONTA_CONTABIL': 'Conta', 'VL_SALDO_FINAL': 'Valor Despesas', 
                                       col_desc: 'Descricao'}, inplace=True)
                    
                    if df['Valor Despesas'].dtype == 'object':
                        df['Valor Despesas'] = df['Valor Despesas'].str.replace(',', '.', regex=False)
                    df['Valor Despesas'] = pd.to_numeric(df['Valor Despesas'], errors='coerce').fillna(0)
                    
                    ano = re.search(r'20\d{2}', file)
                    df['Ano'] = ano.group(0) if ano else '2025'
                    df['Trimestre'] = '1T' if '1T' in file.upper() else ('2T' if '2T' in file.upper() else '3T')
                    
                    cols = ['RegistroANS', 'Ano', 'Trimestre', 'Valor Despesas', 'Descricao']
                    dfs.append(df[[c for c in cols if c in df.columns]])
                    print(f"Lido: {file} ({len(df)} linhas)")
                except: pass
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def enriquecer_final(df_despesas):
    print("\n--- 3. Enriquecimento (JOIN) ---")
    
    garantir_cadastro()
    
    if os.path.exists(ARQUIVO_CADASTRO_LOCAL):
        print(f"-> Lendo arquivo: {ARQUIVO_CADASTRO_LOCAL}")
        df_cad = ler_csv_inteligente(ARQUIVO_CADASTRO_LOCAL)
        
        if df_cad.empty:
            print("ERRO: O arquivo de cadastro parece vazio ou inválido.")
            return df_despesas

        col_map = {c.strip().upper().replace('_', '').replace(' ', ''): c for c in df_cad.columns}
        
        col_registro = None
        # ADICIONEI 'REGISTROOPERADORA' AQUI NA LISTA:
        possiveis_nomes = ['REGISTROOPERADORA', 'REGISTROANS', 'CDOP', 'CODIGO', 'ANS', 'REGISTRO']
        
        for candidato in possiveis_nomes:
            if candidato in col_map:
                col_registro = col_map[candidato]
                print(f"   -> Coluna chave identificada: '{col_registro}'")
                break
        
        if col_registro:
            df_cad.rename(columns={col_registro: 'RegistroANS'}, inplace=True)
            
            for k, v in col_map.items():
                if 'CNPJ' in k: df_cad.rename(columns={v: 'CNPJ'}, inplace=True)
                if 'RAZAO' in k or 'NOME' in k: df_cad.rename(columns={v: 'RazaoSocial'}, inplace=True)
                if k == 'UF': df_cad.rename(columns={v: 'UF'}, inplace=True)

            df_despesas['RegistroANS'] = pd.to_numeric(df_despesas['RegistroANS'], errors='coerce')
            df_cad['RegistroANS'] = pd.to_numeric(df_cad['RegistroANS'], errors='coerce')
            df_cad = df_cad.drop_duplicates(subset=['RegistroANS'])
            
            print("-> Realizando Merge...")
            cols_join = [c for c in ['RegistroANS', 'CNPJ', 'RazaoSocial', 'UF'] if c in df_cad.columns]
            
            df_final = pd.merge(df_despesas, df_cad[cols_join], on='RegistroANS', how='left')
            
            if 'UF' in df_final.columns: df_final['UF'] = df_final['UF'].fillna('N/A')
            
            return df_final
        else:
            print("ERRO CRÍTICO: Não foi possível encontrar a coluna 'RegistroANS' no cadastro.")
            print(f"Colunas disponíveis: {list(df_cad.columns)}")
            return df_despesas
    else:
        print("ERRO: Não foi possível obter o cadastro.")
        return df_despesas

if __name__ == "__main__":
    pasta = os.path.join(os.getcwd(), "downloads_ans")
    
    urls = listar_urls_trimestres()
    for url in urls:
        path = os.path.join(pasta, url.split('/')[-1].replace('.zip',''))
        baixar_e_extrair(url, path)
        
    df = processar_despesas(pasta)
    
    if not df.empty:
        try:
            df_final = enriquecer_final(df)
        except Exception as e:
            print(f"Erro inesperado no enriquecimento: {e}")
            df_final = df
        
        arquivo_csv = "consolidado_despesas.csv"
        df_final.to_csv(arquivo_csv, index=False, sep=';', encoding='utf-8-sig')
        
        with zipfile.ZipFile("consolidado_despesas.zip", 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(arquivo_csv)
            
        print(f"\nSUCESSO TOTAL! {arquivo_csv} gerado.")
        
        cols_view = [c for c in ['RegistroANS', 'CNPJ', 'RazaoSocial', 'UF'] if c in df_final.columns]
        print(df_final[cols_view].head())
    else:
        print("Nenhum dado encontrado.")