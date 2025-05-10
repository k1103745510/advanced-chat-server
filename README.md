# 대화형 API 서버

Flask와 OpenAI API를 사용한 대화형 REST API 서버입니다.

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. `.env` 파일 생성:
- 프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:
```
OPENAI_API_KEY=your_api_key_here
```

## 실행 방법

```bash
python main.py
```

서버가 기본적으로 `http://localhost:5000`에서 실행됩니다.

## API 사용 방법

### POST /query

사용자 입력에 대한 응답을 받습니다.

**요청 형식:**
```json
{
    "input": "사용자 입력 텍스트"
}
```

**응답 형식:**
```json
{
    "response": "OpenAI 응답 텍스트"
}
```

**에러 응답 형식:**
```json
{
    "error": "에러 메시지"
}
```

### GET /history

대화 기록을 조회합니다.

**응답 형식:**
```json
[
    {
        "role": "user",
        "content": "사용자 메시지",
        "timestamp": "2024-03-21T10:30:00.000Z"
    },
    {
        "role": "assistant",
        "content": "어시스턴트 응답",
        "timestamp": "2024-03-21T10:30:01.000Z"
    }
]
```

### DELETE /history

대화 기록을 초기화합니다.

**응답 형식:**
```json
{
    "message": "대화 기록이 초기화되었습니다."
}
```

## 대화 기록 저장

- 모든 대화는 `conversation_history.json` 파일에 자동으로 저장됩니다.
- 서버 재시작 시에도 이전 대화 기록이 유지됩니다.
- 각 메시지에는 타임스탬프가 포함되어 있어 시간 순서를 추적할 수 있습니다. 