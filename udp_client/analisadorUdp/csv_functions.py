import os
import pandas as pd
import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_benchmark_results(directory='.'):
    """
    Plota gráfico de tempo total por execução para diferentes combinações.
    """
    # Encontrar arquivos CSV de benchmark
    csv_files = sorted([
        f for f in os.listdir(directory) 
        if f.startswith('benchmark_results') and f.endswith('.csv')
    ])
    
    # Preparar dados para plotagem
    combinations = [(True, True), (True, False), (False, True), (False, False)]
    plot_data = {combo: [] for combo in combinations}
    
    for filename in csv_files:
        file_path = os.path.join(directory, filename)
        
        try:
            df = pd.read_csv(file_path)
            
            # Verificar se as colunas esperadas existem
            required_columns = ['Print Output', 'Write File', 'Total Time']
            if not all(col in df.columns for col in required_columns):
                print(f"Arquivo {filename} ignorado: colunas necessárias ausentes.")
                continue
            
            # Determinar combinação
            print_output = df['Print Output'].iloc[0]
            write_file = df['Write File'].iloc[0]
            total_time = df['Total Time'].iloc[0]
            
            plot_data[(print_output, write_file)].append(total_time)
        except Exception as e:
            print(f"Erro ao processar {filename}: {e}")
    
    # Plotar gráfico
    plt.figure(figsize=(12, 6))
    
    colors = ['blue', 'green', 'red', 'purple']
    line_styles = ['-', '--', '-.', ':']
    
    for i, ((print_out, write_f), times) in enumerate(plot_data.items()):
        if times:  # Só plota se tiver dados
            plt.plot(
                range(1, len(times) + 1), 
                times, 
                label=f'Print={print_out}, Write={write_f}',
                color=colors[i % len(colors)],
                linestyle=line_styles[i % len(line_styles)]
            )
    
    plt.title('Tempo Total por Execução')
    plt.xlabel('Número de Execuções')
    plt.ylabel('Tempo Total')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('benchmark_total_time.png')
    plt.close()

# Executar plotagem
plot_benchmark_results()

print("Gráfico salvo como benchmark_total_time.png")
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
            print(f"Tempo Total:")
            print(f"  Média: {sum(times)/len(times):.4f}")
            print(f"  Mínimo: {min(times):.4f}")
            print(f"  Máximo: {max(times):.4f}")
    
    return combinations

# Executar análise
analyze_benchmark_results()