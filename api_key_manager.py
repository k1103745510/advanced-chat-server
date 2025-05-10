import os
import json
import secrets
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class APIKeyManager:
    def __init__(self, keys_file: str = 'api_keys.json'):
        self.keys_file = keys_file
        self.keys: Dict[str, Dict] = self._load_keys()

    def _load_keys(self) -> Dict[str, Dict]:
        """API 키 정보를 파일에서 로드합니다."""
        if os.path.exists(self.keys_file):
            try:
                with open(self.keys_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_keys(self) -> None:
        """API 키 정보를 파일에 저장합니다."""
        with open(self.keys_file, 'w', encoding='utf-8') as f:
            json.dump(self.keys, f, ensure_ascii=False, indent=2)

    def generate_key(self, client_name: str, expires_in_days: Optional[int] = None) -> str:
        """새로운 API 키를 생성합니다."""
        api_key = secrets.token_urlsafe(32)
        expires_at = None
        if expires_in_days is not None:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()

        self.keys[api_key] = {
            "client_name": client_name,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "is_active": True
        }
        self._save_keys()
        return api_key

    def validate_key(self, api_key: str) -> bool:
        """API 키의 유효성을 검증합니다."""
        if api_key not in self.keys:
            return False

        key_info = self.keys[api_key]
        if not key_info["is_active"]:
            return False

        if key_info["expires_at"]:
            expires_at = datetime.fromisoformat(key_info["expires_at"])
            if datetime.now() > expires_at:
                return False

        return True

    def revoke_key(self, api_key: str) -> bool:
        """API 키를 비활성화합니다."""
        if api_key in self.keys:
            self.keys[api_key]["is_active"] = False
            self._save_keys()
            return True
        return False

    def list_keys(self) -> List[Dict]:
        """모든 API 키 정보를 반환합니다."""
        return [
            {
                "api_key": key,
                **info
            }
            for key, info in self.keys.items()
        ]

    def get_client_name(self, api_key: str) -> Optional[str]:
        """API 키에 해당하는 클라이언트 이름을 반환합니다."""
        if api_key in self.keys:
            return self.keys[api_key]["client_name"]
        return None 