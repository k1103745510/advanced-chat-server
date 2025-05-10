from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 대화 기록을 저장할 파일 경로
HISTORY_FILE = 'conversation_history.json'

def load_conversation_history():
    """대화 기록을 파일에서 불러옵니다."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_conversation_history(history):
    """대화 기록을 파일에 저장합니다."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# 대화 기록 초기화
conversation_history = load_conversation_history()

@app.route('/query', methods=['POST'])
def query():
    try:
        # JSON 요청 데이터 가져오기
        data = request.get_json()
        if not data or 'input' not in data:
            return jsonify({'error': '입력 데이터가 올바르지 않습니다.'}), 400

        user_input = data['input']
        
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
            model="gpt-4o",
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

        return jsonify({'response': assistant_response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """대화 기록을 조회합니다."""
    try:
        return jsonify(conversation_history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['DELETE'])
def clear_history():
    """대화 기록을 초기화합니다."""
    try:
        global conversation_history
        conversation_history = []
        save_conversation_history(conversation_history)
        return jsonify({'message': '대화 기록이 초기화되었습니다.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 