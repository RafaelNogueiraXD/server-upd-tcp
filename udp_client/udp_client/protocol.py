from enum import Enum, auto

class CommandType(Enum):
    CREATE_SESSION = auto()
    PING = auto()
    UPDATE_DATA = auto()
    CLOSE_SESSION = auto()

def parse_response(response: bytes) -> dict:
    """
    Parseia a resposta do servidor UDP.
    Formato esperado: STATUS|MENSAGEM
    """
    try:
        response_str = response.decode('utf-8')
        parts = response_str.split('|', 1)
        return {
            "status": parts[0],
            "message": parts[1] if len(parts) > 1 else ""
        }
    except Exception:
        return {
            "status": "ERROR", 
            "message": "Invalid response format"
        }