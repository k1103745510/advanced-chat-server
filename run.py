from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from typing import List, Optional, Dict
import hashlib
from api_key_manager import APIKeyManager

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 확인
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

app = FastAPI(
    title="대화형 API 서버",
    description="OpenAI API를 활용한 대화형 REST API 서버",
    version="1.0.0"
)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=api_key)

# API 키 관리자 초기화
api_key_manager = APIKeyManager()

# 대화 기록을 저장할 디렉토리
HISTORY_DIR = 'conversation_histories'
CONFIG_DIR = 'configs'

# 기본 설정
DEFAULT_CONFIG = {
    "model": "gpt-4o"
}

# 디렉토리 생성
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Pydantic 모델 정의
class QueryRequest(BaseModel):
    input: str

class Message(BaseModel):
    role: str
    content: str
    timestamp: str

class QueryResponse(BaseModel):
    response: str

class ErrorResponse(BaseModel):
    error: str

class HistoryResponse(BaseModel):
    message: str

class ModelInfo(BaseModel):
    id: str
    object: str
    created: int
    owned_by: str
    permission: List[Dict]
    root: str
    parent: Optional[str] = None

class ModelsResponse(BaseModel):
    data: List[ModelInfo]
    object: str = "list"

class CurrentModelResponse(BaseModel):
    model: str

class SetModelRequest(BaseModel):
    model: str

class APIKeyRequest(BaseModel):
    client_name: str
    expires_in_days: Optional[int] = None

class APIKeyResponse(BaseModel):
    api_key: str
    client_name: str
    created_at: str
    expires_at: Optional[str]

def get_client_paths(client_id: str) -> tuple[str, str]:
    """클라이언트별 파일 경로를 반환합니다."""
    history_file = os.path.join(HISTORY_DIR, f"{client_id}_history.json")
    config_file = os.path.join(CONFIG_DIR, f"{client_id}_config.json")
    return history_file, config_file

def load_config(client_id: str) -> Dict:
    """클라이언트별 설정을 파일에서 불러옵니다."""
    _, config_file = get_client_paths(client_id)
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(client_id: str, config: Dict) -> None:
    """클라이언트별 설정을 파일에 저장합니다."""
    _, config_file = get_client_paths(client_id)
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_conversation_history(client_id: str) -> List[Message]:
    """클라이언트별 대화 기록을 파일에서 불러옵니다."""
    history_file, _ = get_client_paths(client_id)
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_conversation_history(client_id: str, history: List[Message]) -> None:
    """클라이언트별 대화 기록을 파일에 저장합니다."""
    history_file, _ = get_client_paths(client_id)
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

async def validate_api_key(x_api_key: str = Header(...)) -> str:
    """API 키의 유효성을 검증합니다."""
    if not api_key_manager.validate_key(x_api_key):
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 API 키입니다."
        )
    return x_api_key

@app.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(request: APIKeyRequest):
    """새로운 API 키를 생성합니다."""
    try:
        api_key = api_key_manager.generate_key(
            request.client_name,
            request.expires_in_days
        )
        key_info = api_key_manager.keys[api_key]
        return {
            "api_key": api_key,
            "client_name": key_info["client_name"],
            "created_at": key_info["created_at"],
            "expires_at": key_info["expires_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api-keys/{api_key}", response_model=HistoryResponse)
async def revoke_api_key(api_key: str):
    """API 키를 비활성화합니다."""
    try:
        if api_key_manager.revoke_key(api_key):
            return {"message": "API 키가 비활성화되었습니다."}
        raise HTTPException(status_code=404, detail="API 키를 찾을 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models", response_model=ModelsResponse)
async def get_models(api_key: str = Depends(validate_api_key)):
    """사용 가능한 OpenAI 모델 목록을 조회합니다."""
    try:
        models = client.models.list()
        return {
            "data": models.data,
            "object": "list"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model", response_model=CurrentModelResponse)
async def get_current_model(api_key: str = Depends(validate_api_key)):
    """현재 사용 중인 모델을 조회합니다."""
    try:
        config = load_config(api_key)
        return {"model": config["model"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/model", response_model=CurrentModelResponse)
async def set_model(request: SetModelRequest, api_key: str = Depends(validate_api_key)):
    """사용할 모델을 변경합니다."""
    try:
        # 모델 존재 여부 확인
        models = client.models.list()
        available_models = [model.id for model in models.data]
        
        if request.model not in available_models:
            raise HTTPException(
                status_code=400,
                detail=f"사용할 수 없는 모델입니다. 사용 가능한 모델: {', '.join(available_models)}"
            )
        
        # 모델 변경
        config = load_config(api_key)
        config["model"] = request.model
        save_config(api_key, config)
        
        return {"model": config["model"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse, responses={400: {"model": ErrorResponse}})
async def query(request: QueryRequest, api_key: str = Depends(validate_api_key)):
    try:
        user_input = request.input
        
        # 타임스탬프 추가
        timestamp = datetime.now().isoformat()
        
        # 클라이언트별 대화 기록 로드
        conversation_history = load_conversation_history(api_key)
        
        # 대화 기록에 사용자 입력 추가
        conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })

        # OpenAI API 호출을 위한 메시지 형식 변환
        messages = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in conversation_history
        ]

        # 클라이언트별 설정 로드
        config = load_config(api_key)

        # OpenAI API 호출
        chat_completion = client.chat.completions.create(
            model=config["model"],
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        # 응답 추출
        assistant_response = chat_completion.choices[0].message.content

        # 대화 기록에 어시스턴트 응답 추가
        conversation_history.append({
            "role": "assistant",
            "content": assistant_response,
            "timestamp": datetime.now().isoformat()
        })

        # 대화 기록 저장
        save_conversation_history(api_key, conversation_history)

        return {"response": assistant_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=List[Message])
async def get_history(api_key: str = Depends(validate_api_key)):
    """대화 기록을 조회합니다."""
    try:
        return load_conversation_history(api_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/history", response_model=HistoryResponse)
async def clear_history(api_key: str = Depends(validate_api_key)):
    """대화 기록을 초기화합니다."""
    try:
        save_conversation_history(api_key, [])
        return {"message": "대화 기록이 초기화되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000) 