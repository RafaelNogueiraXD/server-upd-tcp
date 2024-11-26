import socket
import time
import argparse
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
import csv

from .protocol import CommandType, parse_response

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

class UDPClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(5)  # Timeout para recebimento de resposta
        self.session_id: Optional[str] = None

    def _build_message(self, command: CommandType, payload: Optional[str] = None) -> bytes:
        """Constrói mensagem no formato: COMANDO|SESSAO|DADOS"""
        session_part = self.session_id if self.session_id else ""
        payload_part = payload if payload else ""
        message = f"{command.name}|{session_part}|{payload_part}"
        return message.encode('utf-8')

    def send_request(self, command: CommandType, payload: Optional[str] = None) -> dict:
        """Envia um comando e recebe a resposta."""
        try:
            message = self._build_message(command, payload)
            self.socket.sendto(message, (self.host, self.port))
            
            response, _ = self.socket.recvfrom(1024)
            return parse_response(response)
        except socket.timeout:
            return {"status": "ERROR", "message": "Request timed out"}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    def create_session(self) -> bool:
        """Cria uma nova sessão."""
        response = self.send_request(CommandType.CREATE_SESSION)
        if response["status"] == "OK":
            self.session_id = response["message"]
            return True
        return False

    def run_test(
        self,
        num_requests: int,
        use_session: bool,
        print_output: bool,
        write_file: bool,
        output_file: Optional[str] = None
    ) -> TestResult:
        """Executa o teste de desempenho."""
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        output_handler = self._create_output_handler(write_file, output_file) if write_file else None
        
        try:
            # Cria sessão se necessário
            if use_session:
                if not self.create_session():
                    raise Exception("Failed to create session")
            
            start_time = time.time()
            
            for i in range(num_requests):
                request_start = time.time()
                
                if use_session:
                    # Modo com sessão: usa sessão criada
                    response = self.send_request(CommandType.PING)
                else:
                    # Modo sem sessão: recria sessão a cada requisição
                    self.session_id = None
                    response = self.send_request(CommandType.CREATE_SESSION)
                    if response["status"] == "OK":
                        self.session_id = response["message"]
                        response = self.send_request(CommandType.PING)
                
                request_time = time.time() - request_start
                
                if response["status"] == "OK" or response["status"] == "PONG":
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

def run_single_test(args):
    """Executa um único teste com os parâmetros especificados."""
    print(f"Iniciando teste com {args.requests} requisições para {args.host}:{args.port}")
    print(f"Configurações:")
    print(f"- Sessão: {'Sim' if args.session else 'Não'}")
    print(f"- Print: {'Sim' if args.print else 'Não'}")
    print(f"- Arquivo: {'Sim' if args.file else 'Não'}")
    
    client = UDPClient(args.host, args.port)
    
    output_file = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv" if args.file else None
    
    try:
        result = client.run_test(
            args.requests,
            args.session,
            args.print,
            args.file,
            output_file
        )
        
        print(f"\nResultados:")
        print(f"Tempo total: {result.total_time:.2f}s")
        print(f"Requisições/s: {result.requests_per_second:.2f}")
        print(f"Tempo médio de resposta: {result.avg_response_time:.4f}s")
        print(f"Requisições com sucesso: {result.success_requests}")
        print(f"Requisições com falha: {result.failed_requests}")
        
        # Salva o resultado em um arquivo de resultados
        if args.save_results:
            save_results([result], f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            print("\nResultados salvos com sucesso!")
            
    except Exception as e:
        print(f"Erro durante o teste: {e}")

def main():
    parser = argparse.ArgumentParser(description='Cliente UDP para testes de desempenho')
    parser.add_argument('--host', default='localhost', help='Host do servidor')
    parser.add_argument('--port', type=int, default=5000, help='Porta do servidor')
    parser.add_argument('--requests', type=int, default=10000, help='Número de requisições')
    parser.add_argument('--session', action='store_true', help='Usar modo com sessão')
    parser.add_argument('--print', action='store_true', help='Imprimir saída de cada requisição')
    parser.add_argument('--file', action='store_true', help='Salvar saída em arquivo')
    parser.add_argument('--save-results', action='store_true', help='Salvar resultados em arquivo CSV')
    
    args = parser.parse_args()
    
    try:
        run_single_test(args)
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro durante a execução do teste: {e}")

if __name__ == "__main__":
    main()