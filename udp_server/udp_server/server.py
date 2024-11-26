import socket
import threading
import logging
from typing import Tuple

from .session_manager import SessionManager
from .protocols.command_protocol import CommandProtocol, CommandType

class UDPServer:
    def __init__(self, host: str, port: int, max_connections: int = 100):
        self._host = host
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((host, port))
        
        self._session_manager = SessionManager()
        self._max_connections = max_connections
        
        self._active_threads = set()
        
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

    def _handle_client(self, data: bytes, client_addr: Tuple[str, int]):
        """Processa cada mensagem de cliente em uma thread separada."""
        command, session_id, payload = CommandProtocol.parse_command(data)
        
        if not command:
            response = CommandProtocol.create_response('ERROR', 'Invalid Command')
            return self._socket.sendto(response, client_addr)

        try:
            if command == CommandType.CREATE_SESSION:
                new_session_id = self._session_manager.create_session(client_addr)
                response = CommandProtocol.create_response('OK', new_session_id)
            
            elif command == CommandType.PING:
                if self._session_manager.validate_session(session_id):
                    response = CommandProtocol.create_response('PONG', 'Alive')
                else:
                    response = CommandProtocol.create_response('ERROR', 'Invalid Session')
            
            elif command == CommandType.UPDATE_DATA:
                if self._session_manager.validate_session(session_id):
                    self._session_manager.update_session_data(session_id, 'last_ping', payload)
                    response = CommandProtocol.create_response('OK', 'Data Updated')
                else:
                    response = CommandProtocol.create_response('ERROR', 'Invalid Session')
            
            elif command == CommandType.CLOSE_SESSION:
                if self._session_manager.validate_session(session_id):
                    self._session_manager.close_session(session_id)
                    response = CommandProtocol.create_response('OK', 'Session Closed')
                else:
                    response = CommandProtocol.create_response('ERROR', 'Invalid Session')
            
            else:
                response = CommandProtocol.create_response('ERROR', 'Unknown Command')

            self._socket.sendto(response, client_addr)
        
        except Exception as e:
            self._logger.error(f"Error processing command: {e}")
            response = CommandProtocol.create_response('ERROR', str(e))
            self._socket.sendto(response, client_addr)

    def start(self):
        """Inicia o servidor UDP."""
        self._logger.info(f"UDP Server listening on {self._host}:{self._port}")
        
        try:
            while True:
                data, client_addr = self._socket.recvfrom(1024)
                
                # Limita número de threads ativas
                while len(self._active_threads) >= self._max_connections:
                    self._active_threads = {t for t in self._active_threads if t.is_alive()}
                
                thread = threading.Thread(
                    target=self._handle_client, 
                    args=(data, client_addr)
                )
                thread.start()
                self._active_threads.add(thread)
        
        except KeyboardInterrupt:
            self._logger.info("Server shutting down...")
        finally:
            self._socket.close()