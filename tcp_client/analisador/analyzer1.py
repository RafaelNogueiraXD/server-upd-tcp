import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

class TCPResultAnalyzer:
    def __init__(self, results_folder='.'):
        """
        Inicializa o analisador de resultados TCP
        
        :param results_folder: Pasta onde estão os arquivos CSV de resultados
        """
        self.results_folder = results_folder
        self.results_files = []
        self.dataframes = []
    
    def find_result_files(self):
        """
        Encontra todos os arquivos CSV de resultados no diretório
        """
        # Padrões de nomes de arquivos de resultados
        result_patterns = ['benchmark_results_', 'output_']
        
        self.results_files = [
            os.path.join(self.results_folder, f) 
            for f in os.listdir(self.results_folder) 
            if f.endswith('.csv') and 
               any(pattern in f for pattern in result_patterns)
        ]
        
        if not self.results_files:
            print("Nenhum arquivo de resultado encontrado.")
            return []
        
        print(f"Arquivos de resultados encontrados: {self.results_files}")
        return self.results_files
    
    def load_results(self):
        """
        Carrega os arquivos CSV encontrados
        """
        self.dataframes = []
        for file in self.results_files:
            try:
                # Lê o CSV com todos os tipos de dados como string inicialmente
                df = pd.read_csv(file, dtype=str)
                print(f"Colunas no arquivo {file}: {list(df.columns)}")
                
                # Verifica se é um arquivo de benchmark results
                if 'Avg Response Time' in df.columns:
                    # Converte colunas numéricas para float
                    numeric_columns = [
                        'Total Time', 'Requests/s', 'Avg Response Time', 
                        'Total Requests', 'Successful', 'Failed'
                    ]
                    
                    for col in numeric_columns:
                        # Remove qualquer vírgula e converte para float
                        df[col] = df[col].str.replace(',', '.').astype(float)
                    
                    # Renomeia a coluna de tempo de resposta para padronizar
                    df['Response_Time'] = df['Avg Response Time']
                
                self.dataframes.append(df)
                print(f"Arquivo carregado: {file}")
            except Exception as e:
                print(f"Erro ao carregar {file}: {e}")
        
        return self.dataframes
    
    def calculate_statistics(self, df):
        """
        Calcula estatísticas detalhadas para um dataframe
        """
        try:
            # Verifica se há coluna de tempo de resposta
            if 'Response_Time' in df.columns:
                times = df['Response_Time']
                stats_dict = {
                    'Test Configuration': df['Test Type'].iloc[0] if 'Test Type' in df.columns else 'N/A',
                    'Mean Response Time': np.mean(times),
                    'Median Response Time': np.median(times),
                    'Standard Deviation': np.std(times),
                    'Minimum Response Time': np.min(times),
                    'Maximum Response Time': np.max(times),
                }
                
                # Adiciona estatísticas de requisições se disponíveis
                if 'Total Requests' in df.columns:
                    stats_dict.update({
                        'Total Requests': df['Total Requests'].iloc[0],
                        'Successful Requests': df['Successful'].iloc[0],
                        'Failed Requests': df['Failed'].iloc[0],
                        'Requests per Second': df['Requests/s'].iloc[0]
                    })
                
                return stats_dict
        except Exception as e:
            print(f"Erro ao calcular estatísticas: {e}")
        
        return None
    
    def plot_response_times(self):
        """
        Cria gráficos para análise dos tempos de resposta
        """
        # Filtra DataFrames com coluna de tempo de resposta
        valid_dataframes = [df for df in self.dataframes if 'Response_Time' in df.columns]
        
        if not valid_dataframes:
            print("Nenhum DataFrame válido para plotar.")
            return
        
        plt.figure(figsize=(20, 15))
        
        # Preparação dos dados
        test_types = [df['Test Type'].iloc[0] for df in valid_dataframes]
        response_times = [df['Response_Time'] for df in valid_dataframes]
        
        # Boxplot comparativo
        plt.subplot(2, 2, 1)
        plt.boxplot(response_times, labels=test_types)
        plt.title('Tempos de Resposta por Configuração de Teste')
        plt.ylabel('Tempo de Resposta (s)')
        plt.xticks(rotation=45)
        
        # Barras de estatísticas
        plt.subplot(2, 2, 2)
        means = [np.mean(times) for times in response_times]
        stds = [np.std(times) for times in response_times]
        plt.bar(test_types, means, yerr=stds, capsize=10)
        plt.title('Média de Tempos de Resposta com Desvio Padrão')
        plt.ylabel('Tempo Médio de Resposta (s)')
        plt.xticks(rotation=45)
        
        # Gráfico de barras de requisições
        plt.subplot(2, 2, 3)
        successful = [df['Successful'].iloc[0] for df in valid_dataframes]
        failed = [df['Failed'].iloc[0] for df in valid_dataframes]
        
        x = np.arange(len(test_types))
        width = 0.35
        plt.bar(x - width/2, successful, width, label='Successful')
        plt.bar(x + width/2, failed, width, label='Failed')
        plt.title('Requisições Bem-Sucedidas e Falhas')
        plt.xlabel('Configuração de Teste')
        plt.ylabel('Número de Requisições')
        plt.xticks(x, test_types, rotation=45)
        plt.legend()
        
        # Gráfico de requisições por segundo
        plt.subplot(2, 2, 4)
        req_per_sec = [df['Requests/s'].iloc[0] for df in valid_dataframes]
        plt.bar(test_types, req_per_sec)
        plt.title('Requisições por Segundo')
        plt.ylabel('Requisições/s')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig('tcp_performance_analysis.png')
        plt.close()
    
    def generate_report(self):
        """
        Gera relatório completo de estatísticas
        """
        print("\n--- RELATÓRIO DE ANÁLISE DE RESULTADOS ---")
        
        for i, df in enumerate(self.dataframes):
            print(f"\nArquivo {i}:")
            stats = self.calculate_statistics(df)
            if stats:
                for key, value in stats.items():
                    print(f"{key}: {value}")
            else:
                print("Não foi possível calcular estatísticas para este arquivo.")
    
    def run_full_analysis(self):
        """
        Executa análise completa dos resultados
        """
        self.find_result_files()
        self.load_results()
        self.generate_report()
        
        try:
            self.plot_response_times()
            print("\nAnálise concluída. Verifique o arquivo 'tcp_performance_analysis.png'.")
        except Exception as e:
            print(f"Erro ao gerar gráficos: {e}")

def main():
    analyzer = TCPResultAnalyzer()
    analyzer.run_full_analysis()

if __name__ == "__main__":
    main()