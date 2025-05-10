from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from typing import List, Optional

# 환경 변수 로드
load_dotenv()

app = FastAPI(
    title="대화형 API 서버",
    description="OpenAI API를 활용한 대화형 REST API 서버",
    version="1.0.0"
)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 대화 기록을 저장할 파일 경로
HISTORY_FILE = 'conversation_history.json'

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

def load_conversation_history() -> List[Message]:
    """대화 기록을 파일에서 불러옵니다."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_conversation_history(history: List[Message]) -> None:
    """대화 기록을 파일에 저장합니다."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# 대화 기록 초기화
conversation_history = load_conversation_history()

@app.post("/query", response_model=QueryResponse, responses={400: {"model": ErrorResponse}})
async def query(request: QueryRequest):
    try:
        user_input = request.input
        
        # 타임스탬프 추가
        timestamp = datetime.now().isoformat()
        
        # 대화 기록에 사용자 입력 추가
        conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })

        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": msg["role"], "content": msg["content"]} for msg in conversation_history]
        )

        # 응답 추출
        assistant_response = response.choices[0].message.content

        # 대화 기록에 어시스턴트 응답 추가
        conversation_history.append({
            "role": "assistant",
            "content": assistant_response,
            "timestamp": datetime.now().isoformat()
        })

        # 대화 기록 저장
        save_conversation_history(conversation_history)

        return {"response": assistant_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=List[Message])
async def get_history():
    """대화 기록을 조회합니다."""
    try:
        return conversation_history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/history", response_model=HistoryResponse)
async def clear_history():
    """대화 기록을 초기화합니다."""
    try:
        global conversation_history
        conversation_history = []
        save_conversation_history(conversation_history)
        return {"message": "대화 기록이 초기화되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000) 