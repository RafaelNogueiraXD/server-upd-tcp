import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração do estilo dos gráficos
sns.set_theme(style="whitegrid")

# Função para carregar e consolidar arquivos CSV
def load_and_consolidate_benchmark_files(directory="."):
    files = [f for f in os.listdir(directory) if f.startswith("benchmark_results_") and f.endswith(".csv")]
    dataframes = []

    for file in files:
        df = pd.read_csv(os.path.join(directory, file))
        dataframes.append(df)

    return pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()

# Função para criar gráficos
def create_line_or_bar_graphs(data, parameters):
    if data.empty:
        print("Nenhum dado encontrado nos arquivos CSV.")
        return

    for parameter in parameters:
        if parameter not in data.columns:
            print(f"A coluna {parameter} não foi encontrada nos dados.")
            continue

        # Agrupamento dos dados
        grouped = data.groupby(parameter).agg(
            total_time_avg=("Total Time", "mean"),
            total_requests_sum=("Total Requests", "sum")
        ).reset_index()

        # Gráfico de barras
        plt.figure(figsize=(10, 6))
        sns.barplot(x=parameter, y="total_time_avg", data=grouped, palette="viridis")
        plt.title(f"Tempo Total Médio por {parameter}")
        plt.xlabel(parameter)
        plt.ylabel("Tempo Total Médio (s)")
        plt.tight_layout()
        plt.savefig(f"bar_total_time_{parameter.lower().replace(' ', '_')}.png")
        plt.show()

        # Gráfico de linhas
        plt.figure(figsize=(10, 6))
        sns.lineplot(x=parameter, y="total_requests_sum", marker="o", data=grouped, palette="viridis")
        plt.title(f"Total de Requisições por {parameter}")
        plt.xlabel(parameter)
        plt.ylabel("Total de Requisições")
        plt.tight_layout()
        plt.savefig(f"line_total_requests_{parameter.lower().replace(' ', '_')}.png")
        plt.show()

# Main
def main():
    # Substituir o diretório com o caminho onde os arquivos estão armazenados, se necessário
    directory = "."
    data = load_and_consolidate_benchmark_files(directory)

    # Colunas que queremos analisar
    parameters = ["Use Session", "Print Output", "Write File"]
    create_line_or_bar_graphs(data, parameters)

if __name__ == "__main__":
    main()
