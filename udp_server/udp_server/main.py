import os
from dotenv import load_dotenv

from .server import UDPServer

def main():
    # Carrega variáveis de ambiente
    load_dotenv()

    host = os.getenv('UDP_HOST', '127.0.0.1')
    port = int(os.getenv('UDP_PORT', 5000))
    max_connections = int(os.getenv('MAX_CONNECTIONS', 100))

    server = UDPServer(host, port, max_connections)
    server.start()

if __name__ == '__main__':
    main()