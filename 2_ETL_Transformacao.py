import pandas as pd
import zipfile
import os
import re

ARQUIVO_ENTRADA = "consolidado_despesas.csv"
ARQUIVO_SAIDA_CSV = "despesas_agregadas.csv"
ARQUIVO_SAIDA_ZIP = "Teste_Tiago_Rodrigues.zip"

def validar_cnpj(cnpj):
    """Valida formato e matemática do CNPJ."""
    if pd.isna(cnpj): return False
    cnpj = re.sub(r'[^0-9]', '', str(cnpj))
    if len(cnpj) != 14 or cnpj == cnpj[0]*14: return False
    
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d1 = sum(int(cnpj[i]) * pesos1[i] for i in range(12)) % 11
    d1 = 0 if d1 < 2 else 11 - d1
    if int(cnpj[12]) != d1: return False
    
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d2 = sum(int(cnpj[i]) * pesos2[i] for i in range(13)) % 11
    d2 = 0 if d2 < 2 else 11 - d2
    return int(cnpj[13]) == d2

def executar():
    print("--- INICIANDO TESTE 2 (VERSÃO LIMPA) ---")
    
    if not os.path.exists(ARQUIVO_ENTRADA):
        print(f"Erro: {ARQUIVO_ENTRADA} não encontrado. Rode main.py antes.")
        return

    # 1. Carrega (assumindo que main.py fez o trabalho direito)
    print("1. Carregando dados...")
    df = pd.read_csv(ARQUIVO_ENTRADA, sep=';', encoding='utf-8-sig')
    
    # 2. Validação
    print("2. Validando dados...")
    df['CNPJ_Valido'] = df['CNPJ'].apply(validar_cnpj)
    df['Valor Despesas'] = pd.to_numeric(df['Valor Despesas'], errors='coerce').fillna(0)
    df['Valor_Valido'] = df['Valor Despesas'] > 0
    
    # Filtro
    df_clean = df[df['CNPJ_Valido'] & df['Valor_Valido']].copy()
    print(f"   Total: {len(df)} -> Válidos: {len(df_clean)}")
    
    # 3. Agregação
    print("3. Gerando estatísticas...")
    if 'UF' not in df_clean.columns: df_clean['UF'] = 'N/A'
    df_clean['UF'] = df_clean['UF'].fillna('N/A')
    
    df_agg = df_clean.groupby(['RazaoSocial', 'UF']).agg({
        'Valor Despesas': ['sum', 'mean', 'std', 'count']
    })
    
    df_agg.columns = ['Valor_Total', 'Media_Trimestral', 'Desvio_Padrao', 'Qtd_Registros']
    df_agg = df_agg.reset_index()
    
    # Formatação
    df_agg['Valor_Total'] = df_agg['Valor_Total'].round(2)
    df_agg['Media_Trimestral'] = df_agg['Media_Trimestral'].round(2)
    df_agg['Desvio_Padrao'] = df_agg['Desvio_Padrao'].fillna(0).round(2)
    df_agg.sort_values(by='Valor_Total', ascending=False, inplace=True)
    
    # 4. Salvar
    print("4. Salvando...")
    df_agg.to_csv(ARQUIVO_SAIDA_CSV, index=False, sep=';', encoding='utf-8-sig')
    
    with zipfile.ZipFile(ARQUIVO_SAIDA_ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(ARQUIVO_SAIDA_CSV)
        
    print(f"\nSUCESSO! Zip gerado: {ARQUIVO_SAIDA_ZIP}")
    print(df_agg.head())

if __name__ == "__main__":
    executar()