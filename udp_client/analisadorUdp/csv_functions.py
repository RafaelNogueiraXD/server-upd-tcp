import os
import pandas as pd
import numpy as np
def analyze_benchmark_results(directory='.'):
    """
    Analisa arquivos de benchmark e conta combinações de Print Output e Write File.
    """
    # Encontrar arquivos CSV de benchmark
    csv_files = sorted([f for f in os.listdir(directory) 
                        if f.startswith('benchmark_results') and f.endswith('.csv')])
    
    # Contagem de combinações
    combinations = {
        (True, True): [],
        (True, False): [],
        (False, True): [],
        (False, False): []
    }
    
    for filename in csv_files:
        file_path = os.path.join(directory, filename)
        df = pd.read_csv(file_path)
        
        # Determinar combinação
        print_output = df['Print Output'].iloc[0]
        write_file = df['Write File'].iloc[0]
        total_time = df['Total Time'].iloc[0]
        
        # Adicionar dados à combinação
        combinations[(print_output, write_file)].append({
            'filename': filename,
            'total_time': total_time
        })
    
    # Imprimir relatório detalhado
    print("\n--- Relatório de Benchmark ---")
    for (print_out, write_f), data in combinations.items():
        print(f"\nCombinação - Print Output = {print_out}, Write File = {write_f}:")
        print(f"Número de arquivos: {len(data)}")
        
        if data:
            times = [item['total_time'] for item in data]
            
            # Cálculos estatísticos
            mean_time = np.mean(times)
            median_time = np.median(times)
            std_time = np.std(times)
            
            print(f"Tempo Total:")
            print(f"  Média:     {mean_time:.4f}")
            print(f"  Mediana:   {median_time:.4f}")
            print(f"  Mínimo:    {min(times):.4f}")
            print(f"  Máximo:    {max(times):.4f}")
            print(f"  Desvio Padrão: {std_time:.4f}")
    
    return combinations

# Executar análise
analyze_benchmark_results()