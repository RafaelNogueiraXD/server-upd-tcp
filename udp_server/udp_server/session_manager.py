import uuid
from typing import Dict, Any
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self, timeout_seconds: int = 3600):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._timeout = timeout_seconds

    def create_session(self, client_addr: tuple) -> str:
        """Cria uma nova sessão para o cliente."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            'client_addr': client_addr,
            'created_at': datetime.now(),
            'data': {}
        }
        return session_id

    def validate_session(self, session_id: str) -> bool:
        """Valida se a sessão existe e não expirou."""
        if session_id not in self._sessions:
            return False

        session = self._sessions[session_id]
        elapsed_time = datetime.now() - session['created_at']
        
        if elapsed_time > timedelta(seconds=self._timeout):
            del self._sessions[session_id]
            return False
        
        return True

    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Retorna os dados da sessão."""
        return self._sessions.get(session_id, {}).get('data', {})

    def update_session_data(self, session_id: str, key: str, value: Any):
        """Atualiza um dado específico na sessão."""
        if self.validate_session(session_id):
            self._sessions[session_id]['data'][key] = value

    def close_session(self, session_id: str):
        """Encerra uma sessão."""
        if session_id in self._sessions:
            del self._sessions[session_id]