import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração do estilo de gráficos
sns.set_theme(style="whitegrid")

# Função para carregar os arquivos CSV
def load_statistics(file_path):
    return pd.read_csv(file_path)

# Função para comparar as estatísticas
def compare_statistics(tcp_stats, udp_stats, group_columns, metric_columns):
    comparison = pd.merge(
        tcp_stats,
        udp_stats,
        on=group_columns,
        suffixes=("_tcp", "_udp"),
        how="inner"
    )
    return comparison

# Função para gerar gráficos de comparação
def plot_comparison(comparison, group_column, metric_column):
    plt.figure(figsize=(10, 6))
    comparison_long = comparison.melt(
        id_vars=group_column,
        value_vars=[f"{metric_column}_tcp", f"{metric_column}_udp"],
        var_name="Server Type",
        value_name=metric_column
    )
    sns.barplot(
        x=group_column, y=metric_column, hue="Server Type", data=comparison_long, palette="viridis"
    )
    plt.title(f"Comparação de {metric_column} - TCP vs UDP")
    plt.xlabel(group_column)
    plt.ylabel(metric_column)
    plt.tight_layout()
    plt.savefig(f"comparison_{metric_column.lower()}_{group_column.lower()}.png")
    plt.show()

# Main
def main():
    # Caminhos dos arquivos benchmark_statistics.csv
    tcp_file = "benchmark_statistics_tcp.csv"
    udp_file = "benchmark_statistics_udp.csv"

    # Carregar os dados
    tcp_stats = load_statistics(tcp_file)
    udp_stats = load_statistics(udp_file)

    # Colunas para agrupar e métricas para comparar
    group_columns = ["Use Session", "Print Output", "Write File"]
    metric_columns = ["mean_time", "median_time", "std_time", "min_time", "max_time"]

    # Comparar as estatísticas
    comparison = compare_statistics(tcp_stats, udp_stats, group_columns, metric_columns)

    # Gerar gráficos para cada métrica
    for metric in metric_columns:
        plot_comparison(comparison, "Use Session", metric)
        plot_comparison(comparison, "Print Output", metric)
        plot_comparison(comparison, "Write File", metric)

    # Salvar a tabela de comparação como CSV
    output_file = "benchmark_comparison.csv"
    comparison.to_csv(output_file, index=False)
    print(f"Tabela de comparação salva em: {output_file}")

if __name__ == "__main__":
    main()
