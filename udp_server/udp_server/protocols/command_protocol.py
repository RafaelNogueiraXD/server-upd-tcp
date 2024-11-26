from enum import Enum, auto

class CommandType(Enum):
    CREATE_SESSION = auto()
    PING = auto()
    UPDATE_DATA = auto()
    CLOSE_SESSION = auto()

class CommandProtocol:
    @staticmethod
    def parse_command(message: bytes) -> tuple:
        """
        Parseia mensagens UDP de acordo com o protocolo.
        Formato: COMANDO|SESSAO|DADOS
        """
        try:
            parts = message.decode('utf-8').split('|')
            command = CommandType[parts[0]]
            session_id = parts[1] if len(parts) > 1 else None
            data = parts[2] if len(parts) > 2 else None
            
            return command, session_id, data
        except (IndexError, KeyError):
            return None, None, None

    @staticmethod
    def create_response(status: str, message: str) -> bytes:
        """Cria uma resposta padronizada."""
        return f"{status}|{message}".encode('utf-8')