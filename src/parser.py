import pandas as pd
import csv
import os

def detect_delimiter(file_path):
    """Detecta automaticamente o delimitador do CSV de forma robusta."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        # Lê as primeiras 50 linhas para análise de estrutura
        lines = [f.readline() for _ in range(50)]
        
        # Encontra a linha que parece ser o cabeçalho dos dados
        data_line = ""
        for line in lines:
            if not line.strip() or line.startswith('['):
                continue
            # Se a linha tem muitos números ou vírgulas/ponto-e-vírgula, é candidata
            if any(char in line for char in ',;'):
                data_line = line
                break
        
        if not data_line:
            return ','
            
        # Tenta detectar o delimitador mais comum na linha candidata
        comma_count = data_line.count(',')
        semicolon_count = data_line.count(';')
        
        return ';' if semicolon_count > comma_count else ','

def load_csv_data(file_path):
    """Lê arquivos CSV de forma genérica, pulando metadados e detectando colunas."""
    delimiter = detect_delimiter(file_path)
    
    skip_rows = 0
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            # Detecta o início dos dados reais (padrão [Data] ou primeira linha com delimitador)
            if '[Data]' in line:
                skip_rows = i + 1
                break
            # Se encontrar uma linha com delimitador e sem caracteres de metadados '['
            if delimiter in line and not line.startswith('['):
                skip_rows = i
                break
    
    try:
        # Lê o CSV, removendo espaços em branco dos nomes das colunas
        df = pd.read_csv(file_path, skiprows=skip_rows, delimiter=delimiter, skipinitialspace=True)
        # Limpa colunas vazias ou nomes nulos
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        print(f"    [Aviso] Erro ao ler {os.path.basename(file_path)}: {e}")
        return None

def get_all_csvs(data_dir):
    """Lista todos os arquivos CSV em uma pasta."""
    if not os.path.exists(data_dir):
        return []
    return sorted([os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')])
