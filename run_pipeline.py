import os
import time

def run_step(script_name, step_name):
    print(f"\n>>> INICIANDO ETAPA: {step_name} ({script_name})")
    exit_code = os.system(f".\\venv\\Scripts\\python.exe {script_name}")
    
    if exit_code == 0:
        print(f">>> SUCESSO na etapa: {step_name}")
        return True
    else:
        print(f">>> ERRO na etapa: {step_name}. Processo interrompido.")
        return False

if __name__ == "__main__":
    print("=== ORQUESTRADOR DE PIPELINE INTUITIVE CARE ===")
    
    # 1. ETL - Crawler
    if not run_step("1_ETL_Crawler.py", "Extração de Dados (Web Scraping)"): exit()
    
    # 2. ETL - Transformação
    if not run_step("2_ETL_Transformacao.py", "Limpeza e Validação"): exit()
    
    # 3. Banco de Dados
    if not run_step("3_SQL_Database.py", "Geração de Scripts SQL"): exit()
    
    print("\n=== PIPELINE DE DADOS CONCLUÍDO COM SUCESSO! ===")
    print("Agora você pode iniciar a API e abrir o Dashboard.")
    print("Para iniciar a API, rode: .\\venv\\Scripts\\python.exe -m uvicorn 4_Backend_API:app --reload")