from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import openai
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from typing import List, Optional, Dict

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 확인
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

# API 키 검증을 위한 의존성 함수
async def verify_api_key(x_api_key: str = Header(..., description="API 키")):
    """API 키를 검증합니다."""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API 키가 필요합니다."
        )
    
    # 환경 변수에서 API 키 가져오기
    valid_api_key = os.getenv('API_KEY')
    if not valid_api_key:
        raise HTTPException(
            status_code=500,
            detail="서버 설정 오류: API 키가 설정되지 않았습니다."
        )
    
    if x_api_key != valid_api_key:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 API 키입니다."
        )
    
    return x_api_key

app = FastAPI(
    title="대화형 API 서버",
    description="OpenAI API를 활용한 대화형 REST API 서버",
    version="1.0.0"
)

# OpenAI 클라이언트 초기화
client = openai.OpenAI()

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
    client_name: str

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
    client_name: str

def get_client_paths(client_name: str) -> tuple[str, str]:
    """클라이언트별 파일 경로를 반환합니다."""
    history_file = os.path.join(HISTORY_DIR, f"{client_name}_history.json")
    config_file = os.path.join(CONFIG_DIR, f"{client_name}_config.json")
    return history_file, config_file

def load_config(client_name: str) -> Dict:
    """클라이언트별 설정을 파일에서 불러옵니다."""
    _, config_file = get_client_paths(client_name)
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(client_name: str, config: Dict) -> None:
    """클라이언트별 설정을 파일에 저장합니다."""
    _, config_file = get_client_paths(client_name)
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_conversation_history(client_name: str) -> List[Message]:
    """클라이언트별 대화 기록을 파일에서 불러옵니다."""
    history_file, _ = get_client_paths(client_name)
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_conversation_history(client_name: str, history: List[Message]) -> None:
    """클라이언트별 대화 기록을 파일에 저장합니다."""
    history_file, _ = get_client_paths(client_name)
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

@app.get("/models", response_model=ModelsResponse)
async def get_models(api_key: str = Depends(verify_api_key)):
    """사용 가능한 OpenAI 모델 목록을 조회합니다."""
    try:
        response = client.models.list()
        return {
            "data": [
                {
                    "id": model.id,
                    "object": model.object,
                    "created": model.created,
                    "owned_by": model.owned_by,
                    "permission": getattr(model, 'permission', []),
                    "root": getattr(model, 'root', model.id),
                    "parent": getattr(model, 'parent', None)
                }
                for model in response.data
            ],
            "object": "list"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model", response_model=CurrentModelResponse)
async def get_current_model(client_name: str, api_key: str = Depends(verify_api_key)):
    """현재 사용 중인 모델을 조회합니다."""
    try:
        config = load_config(client_name)
        return {"model": config["model"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/model", response_model=CurrentModelResponse)
async def set_model(request: SetModelRequest, api_key: str = Depends(verify_api_key)):
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
        config = load_config(request.client_name)
        config["model"] = request.model
        save_config(request.client_name, config)
        
        return {"model": config["model"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse, responses={400: {"model": ErrorResponse}})
async def query(request: QueryRequest, api_key: str = Depends(verify_api_key)):
    try:
        user_input = request.input
        client_name = request.client_name
        
        # 타임스탬프 추가
        timestamp = datetime.now().isoformat()
        
        # 클라이언트별 대화 기록 로드
        conversation_history = load_conversation_history(client_name)
        
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
        config = load_config(client_name)

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
        save_conversation_history(client_name, conversation_history)

        return {"response": assistant_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=List[Message])
async def get_history(client_name: str, api_key: str = Depends(verify_api_key)):
    """대화 기록을 조회합니다."""
    try:
        return load_conversation_history(client_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/history", response_model=HistoryResponse)
async def clear_history(client_name: str, api_key: str = Depends(verify_api_key)):
    """대화 기록을 초기화합니다."""
    try:
        save_conversation_history(client_name, [])
        return {"message": "대화 기록이 초기화되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000) 