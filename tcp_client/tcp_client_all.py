# tcp_client.py
import socket
import json
import time
import argparse
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime
import csv
import concurrent.futures

@dataclass
class TestResult:
    test_type: str
    total_time: float
    requests_per_second: float
    avg_response_time: float
    total_requests: int
    success_requests: int
    failed_requests: int
    use_session: bool
    print_output: bool
    write_file: bool
    timestamp: str

class TCPClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.session_socket: Optional[socket.socket] = None
        
    def connect(self) -> socket.socket:
        """Cria uma nova conexão TCP."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Adiciona a opção de reutilização do socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.connect((self.host, self.port))
            return sock
        except Exception as e:
            sock.close()
            raise e
        
    def send_request(self, sock: socket.socket, command: str) -> dict:
        """Envia um comando e recebe a resposta."""
        try:
            sock.send(f"{command}\n".encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            return json.loads(response)
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
            
    def run_test(
        self,
        num_requests: int,
        use_session: bool,
        print_output: bool,
        write_file: bool,
        output_file: Optional[str] = None
    ) -> TestResult:
        """Executa o teste de desempenho com os parâmetros especificados."""
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        output_handler = self._create_output_handler(write_file, output_file) if write_file else None
        
        try:
            start_time = time.time()
            
            if use_session:
                # Modo com sessão: uma única conexão
                sock = self.connect()
                try:
                    for i in range(num_requests):
                        request_start = time.time()
                        response = self.send_request(sock, "PING")
                        request_time = time.time() - request_start
                        
                        if response["status"] == "OK":
                            successful_requests += 1
                        else:
                            failed_requests += 1
                        
                        response_times.append(request_time)
                        
                        if print_output:
                            print(f"Request {i + 1}: {response} ({request_time:.4f}s)")
                        
                        if output_handler:
                            output_handler.write(
                                f"{i + 1},{response['status']},{request_time:.4f}\n"
                            )
                finally:
                    sock.close()
                    time.sleep(0.1)  # Pequena pausa para garantir que o socket seja fechado
            else:
                # Modo sem sessão: uma conexão por requisição
                for i in range(num_requests):
                    request_start = time.time()
                    try:
                        sock = self.connect()
                        try:
                            response = self.send_request(sock, "PING")
                            request_time = time.time() - request_start
                            
                            if response["status"] == "OK":
                                successful_requests += 1
                            else:
                                failed_requests += 1
                            
                            response_times.append(request_time)
                            
                            if print_output:
                                print(f"Request {i + 1}: {response} ({request_time:.4f}s)")
                            
                            if output_handler:
                                output_handler.write(
                                    f"{i + 1},{response['status']},{request_time:.4f}\n"
                                )
                        finally:
                            sock.close()
                            time.sleep(0.01)  # Pequena pausa entre conexões
                    except Exception as e:
                        if print_output:
                            print(f"Error in request {i + 1}: {e}")
                        failed_requests += 1
                        time.sleep(0.1)  # Pausa maior em caso de erro
            
            total_time = time.time() - start_time
            
            return TestResult(
                test_type="Session" if use_session else "No Session",
                total_time=total_time,
                requests_per_second=num_requests / total_time,
                avg_response_time=sum(response_times) / len(response_times) if response_times else 0,
                total_requests=num_requests,
                success_requests=successful_requests,
                failed_requests=failed_requests,
                use_session=use_session,
                print_output=print_output,
                write_file=write_file,
                timestamp=datetime.now().isoformat()
            )
            
        finally:
            if output_handler:
                output_handler.close()
    
    def _create_output_handler(self, write_file: bool, filename: Optional[str]) -> Optional[object]:
        """Cria um manipulador de arquivo para saída."""
        if write_file and filename:
            return open(filename, 'w', newline='')
        return None

def save_results(results: List[TestResult], filename: str):
    """Salva os resultados dos testes em um arquivo CSV."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Test Type', 'Total Time', 'Requests/s', 'Avg Response Time',
            'Total Requests', 'Successful', 'Failed', 'Use Session',
            'Print Output', 'Write File', 'Timestamp'
        ])
        
        for result in results:
            writer.writerow([
                result.test_type,
                f"{result.total_time:.2f}",
                f"{result.requests_per_second:.2f}",
                f"{result.avg_response_time:.4f}",
                result.total_requests,
                result.success_requests,
                result.failed_requests,
                result.use_session,
                result.print_output,
                result.write_file,
                result.timestamp
            ])

def run_all_tests(args):
    """Executa todas as combinações de testes."""
    print(f"Iniciando testes com {args.requests} requisições para {args.host}:{args.port}")
    
    client = TCPClient(args.host, args.port)
    results = []
    
    # Todas as combinações possíveis
    combinations = [
        (True, True, True),
        (True, True, False),
        (True, False, True),
        (True, False, False),
        (False, True, True),
        (False, True, False),
        (False, False, True),
        (False, False, False),
    ]
    
    for use_session, print_output, write_file in combinations:
        output_file = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv" if write_file else None
        
        print(f"\nExecutando teste:")
        print(f"- Sessão: {'Sim' if use_session else 'Não'}")
        print(f"- Print: {'Sim' if print_output else 'Não'}")
        print(f"- Arquivo: {'Sim' if write_file else 'Não'}")
        
        try:
            result = client.run_test(
                args.requests,
                use_session,
                print_output,
                write_file,
                output_file
            )
            
            results.append(result)
            
            print(f"\nResultados:")
            print(f"Tempo total: {result.total_time:.2f}s")
            print(f"Requisições/s: {result.requests_per_second:.2f}")
            print(f"Tempo médio de resposta: {result.avg_response_time:.4f}s")
            print(f"Requisições com sucesso: {result.success_requests}")
            print(f"Requisições com falha: {result.failed_requests}")
            
            # Pausa entre testes
            time.sleep(1)
            
        except Exception as e:
            print(f"Erro durante o teste: {e}")
            continue
    
    # Salva todos os resultados
    try:
        save_results(results, f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        print("\nResultados salvos com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar resultados: {e}")

def main():
    parser = argparse.ArgumentParser(description='Cliente TCP para testes de desempenho')
    parser.add_argument('--host', default='127.0.0.1', help='Host do servidor')
    parser.add_argument('--port', type=int, default=5000, help='Porta do servidor')
    parser.add_argument('--requests', type=int, default=10000, help='Número de requisições')
    
    args = parser.parse_args()
    
    try:
        run_all_tests(args)
    except KeyboardInterrupt:
        print("\nTestes interrompidos pelo usuário.")
    except Exception as e:
        print(f"\nErro durante a execução dos testes: {e}")

if __name__ == "__main__":
    main()