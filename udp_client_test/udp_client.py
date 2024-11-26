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

class UDPClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.session_socket: Optional[socket.socket] = None
        
    def create_socket(self) -> socket.socket:
        """Create a new UDP socket with enhanced configurations."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Increase receive buffer size
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1024)
        
        # Set more flexible timeout
        sock.settimeout(2.0)
        
        return sock
        
    def send_request(self, sock: socket.socket, command: str) -> dict:
        """Send a command and receive a response with detailed error handling."""
        try:
            # Encode and send the command
            message = f"{command}\n".encode('utf-8')
            sock.sendto(message, (self.host, self.port))
            
            try:
                # Attempt to receive response
                response, address = sock.recvfrom(4096)
                
                # Decode and parse response
                decoded_response = response.decode('utf-8').strip()
                
                try:
                    return json.loads(decoded_response)
                except json.JSONDecodeError:
                    # If JSON decoding fails, create a custom response
                    return {
                        "status": "ERROR", 
                        "message": f"Invalid JSON response: {decoded_response}"
                    }
            
            except socket.timeout:
                return {"status": "TIMEOUT", "message": "Request timed out"}
            except ConnectionResetError:
                return {"status": "RESET", "message": "Connection reset by peer"}
        
        except Exception as e:
            return {"status": "ERROR", "message": f"Unexpected error: {str(e)}"}
            
    def run_test(
        self,
        num_requests: int,
        use_session: bool,
        print_output: bool,
        write_file: bool,
        output_file: Optional[str] = None
    ) -> TestResult:
        """Execute performance test with specified parameters and improved logging."""
        successful_requests = 0
        failed_requests = 0
        response_times = []
        error_types = {}
        
        output_handler = self._create_output_handler(write_file, output_file) if write_file else None
        
        try:
            start_time = time.time()
            
            if use_session:
                # Session mode: single socket for all requests
                sock = self.create_socket()
                try:
                    for i in range(num_requests):
                        request_start = time.time()
                        response = self.send_request(sock, "PING")
                        request_time = time.time() - request_start
                        
                        if response["status"] == "OK":
                            successful_requests += 1
                        else:
                            failed_requests += 1
                            error_types[response["status"]] = error_types.get(response["status"], 0) + 1
                        
                        response_times.append(request_time)
                        
                        if print_output:
                            print(f"Request {i + 1}: {response} ({request_time:.4f}s)")
                        
                        if output_handler:
                            output_handler.write(
                                f"{i + 1},{response['status']},{request_time:.4f},{response.get('message', '')}\n"
                            )
                finally:
                    sock.close()
            else:
                # No session mode: new socket for each request
                for i in range(num_requests):
                    request_start = time.time()
                    sock = self.create_socket()
                    try:
                        response = self.send_request(sock, "PING")
                        request_time = time.time() - request_start
                        
                        if response["status"] == "OK":
                            successful_requests += 1
                        else:
                            failed_requests += 1
                            error_types[response["status"]] = error_types.get(response["status"], 0) + 1
                        
                        response_times.append(request_time)
                        
                        if print_output:
                            print(f"Request {i + 1}: {response} ({request_time:.4f}s)")
                        
                        if output_handler:
                            output_handler.write(
                                f"{i + 1},{response['status']},{request_time:.4f},{response.get('message', '')}\n"
                            )
                    except Exception as e:
                        failed_requests += 1
                        if print_output:
                            print(f"Error in request {i + 1}: {e}")
                    finally:
                        sock.close()
            
            total_time = time.time() - start_time
            
            result = TestResult(
                test_type="Session" if use_session else "No Session",
                total_time=total_time,
                requests_per_second=num_requests / total_time if total_time > 0 else 0,
                avg_response_time=sum(response_times) / len(response_times) if response_times else 0,
                total_requests=num_requests,
                success_requests=successful_requests,
                failed_requests=failed_requests,
                use_session=use_session,
                print_output=print_output,
                write_file=write_file,
                timestamp=datetime.now().isoformat()
            )
            
            # Print detailed error information
            if failed_requests > 0:
                print("\nError Types:")
                for error_type, count in error_types.items():
                    print(f"- {error_type}: {count} times")
            
            return result
            
        finally:
            if output_handler:
                output_handler.close()
    
    def _create_output_handler(self, write_file: bool, filename: Optional[str]) -> Optional[object]:
        """Create a file handler for output."""
        if write_file and filename:
            return open(filename, 'w', newline='')
        return None

def save_results(results: List[TestResult], filename: str):
    """Save test results to a CSV file."""
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
    """Execute a single test with specified parameters and enhanced diagnostics."""
    print(f"Starting UDP test with {args.requests} requests to {args.host}:{args.port}")
    print(f"Settings:")
    print(f"- Session: {'Yes' if args.session else 'No'}")
    print(f"- Print: {'Yes' if args.print else 'No'}")
    print(f"- File: {'Yes' if args.file else 'No'}")
    
    # Diagnostic socket connection test
    try:
        diagnostic_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        diagnostic_socket.settimeout(2.0)
        diagnostic_socket.sendto(b"DIAGNOSTIC_TEST", (args.host, args.port))
        try:
            diagnostic_socket.recvfrom(1024)
            print("\n[DIAGNOSTIC] Initial socket connection successful!")
        except socket.timeout:
            print("\n[WARNING] Diagnostic socket test timed out. Server might not be responding.")
        except Exception as e:
            print(f"\n[WARNING] Diagnostic socket test failed: {e}")
        finally:
            diagnostic_socket.close()
    except Exception as e:
        print(f"\n[ERROR] Could not create diagnostic socket: {e}")
    
    client = UDPClient(args.host, args.port)
    
    output_file = f"udp_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv" if args.file else None
    
    try:
        result = client.run_test(
            args.requests,
            args.session,
            args.print,
            args.file,
            output_file
        )
        
        print(f"\nResults:")
        print(f"Total time: {result.total_time:.2f}s")
        print(f"Requests/s: {result.requests_per_second:.2f}")
        print(f"Average response time: {result.avg_response_time:.4f}s")
        print(f"Successful requests: {result.success_requests}")
        print(f"Failed requests: {result.failed_requests}")
        
        # Save results to a file
        if args.save_results:
            save_results([result], f"udp_benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            print("\nResults saved successfully!")
            
    except Exception as e:
        print(f"Error during test: {e}")

def main():
    parser = argparse.ArgumentParser(description='UDP Client for Performance Testing')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=5000, help='Server port')
    parser.add_argument('--requests', type=int, default=10000, help='Number of requests')
    parser.add_argument('--session', action='store_true', help='Use session mode')
    parser.add_argument('--print', action='store_true', help='Print output for each request')
    parser.add_argument('--file', action='store_true', help='Save output to file')
    parser.add_argument('--save-results', action='store_true', help='Save results to CSV')
    
    args = parser.parse_args()
    
    try:
        run_single_test(args)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nError during test execution: {e}")

if __name__ == "__main__":
    main()