import os
import pandas as pd

# Função para carregar e consolidar arquivos CSV
def load_and_consolidate_benchmark_files(directory="."):
    files = [f for f in os.listdir(directory) if f.startswith("benchmark_results_") and f.endswith(".csv")]
    dataframes = []

    for file in files:
        df = pd.read_csv(os.path.join(directory, file))
        dataframes.append(df)

    return pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()

# Função para calcular estatísticas
def calculate_statistics(data, group_columns):
    if data.empty:
        print("Nenhum dado encontrado nos arquivos CSV.")
        return pd.DataFrame()

    statistics = (
        data.groupby(group_columns)["Total Time"]
        .agg(
            mean_time="mean",
            median_time="median",
            std_time="std",
            min_time="min",
            max_time="max"
        )
        .reset_index()
    )
    return statistics

# Main
def main():
    # Substituir o diretório com o caminho onde os arquivos estão armazenados, se necessário
    directory = "."
    data = load_and_consolidate_benchmark_files(directory)

    # Colunas que queremos analisar
    group_columns = ["Use Session", "Print Output", "Write File"]

    # Calculando estatísticas
    statistics = calculate_statistics(data, group_columns)

    # Salvar os resultados em um arquivo CSV
    if not statistics.empty:
        output_file = "benchmark_statistics.csv"
        statistics.to_csv(output_file, index=False)
        print(f"Estatísticas salvas em: {output_file}")
    else:
        print("Não foi possível calcular estatísticas devido à falta de dados.")

if __name__ == "__main__":
    main()
