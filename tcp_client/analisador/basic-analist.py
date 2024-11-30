import os
import pandas as pd
import numpy as np
import itertools

def analyze_benchmark_results(directory='.'):
    """
    Analisa arquivos de benchmark com múltiplas execuções por arquivo.
    Calcula estatísticas para cada combinação de parâmetros.
    """
    # Encontrar arquivos CSV de benchmark
    csv_files = sorted([f for f in os.listdir(directory) 
                        if f.startswith('benchmark_results') and f.endswith('.csv')])
    
    # Dicionário para armazenar todas as combinações de resultados
    combinations = {}
    
    # Processar cada arquivo CSV
    for filename in csv_files:
        file_path = os.path.join(directory, filename)
        df = pd.read_csv(file_path)
        
        # Criar chave de combinação para cada linha
        for _, row in df.iterrows():
            key = (
                row['Use Session'], 
                row['Print Output'], 
                row['Write File']
            )
            
            # Inicializar a chave se não existir
            if key not in combinations:
                combinations[key] = []
            
            # Adicionar dados desta execução
            combinations[key].append({
                'filename': filename,
                'total_time': row['Total Time'],
                'requests_per_sec': row['Requests/s'],
                'avg_response_time': row['Avg Response Time'],
                'total_requests': row['Total Requests'],
                'successful': row['Successful'],
                'failed': row['Failed'],
                'timestamp': row['Timestamp']
            })
    
    # Imprimir relatório detalhado
    print("\n--- Relatório de Benchmark ---")
    for key, data in sorted(combinations.items()):
        use_session, print_output, write_file = key
        
        print(f"\nCombinação:")
        print(f"  Use Session:    {use_session}")
        print(f"  Print Output:   {print_output}")
        print(f"  Write File:     {write_file}")
        print(f"  Número de execuções: {len(data)}")
        
        # Extrair métricas para análise
        total_times = [entry['total_time'] for entry in data]
        requests_per_sec = [entry['requests_per_sec'] for entry in data]
        avg_response_times = [entry['avg_response_time'] for entry in data]
        
        # Calcular estatísticas
        def print_stats(values, metric_name):
            print(f"\n  {metric_name}:")
            print(f"    Média:         {np.mean(values):.4f}")
            print(f"    Mediana:       {np.median(values):.4f}")
            print(f"    Mínimo:        {min(values):.4f}")
            print(f"    Máximo:        {max(values):.4f}")
            print(f"    Desvio Padrão: {np.std(values):.4f}")
        
        # Imprimir estatísticas
        print_stats(total_times, "Tempo Total (s)")
        print_stats(requests_per_sec, "Requisições por Segundo")
        print_stats(avg_response_times, "Tempo Médio de Resposta (s)")
        
        # Informações adicionais
        total_requests = data[0]['total_requests']
        successful = sum(entry['successful'] for entry in data)
        failed = sum(entry['failed'] for entry in data)
        
        print("\n  Resumo de Requisições:")
        print(f"    Total por Execução: {total_requests}")
        print(f"    Total Successful:   {successful}")
        print(f"    Total Failed:       {failed}")
    
    return combinations

# Executar análise
analyze_benchmark_results()