# 대화형 API 서버

OpenAI API를 활용한 대화형 REST API 서버입니다.

## 기능

- OpenAI API를 통한 대화형 응답 생성
- 클라이언트별 대화 기록 관리
- 사용 가능한 모델 목록 조회
- 모델 변경 기능

## 설치 및 실행

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:
`.env` 파일을 생성하고 OpenAI API 키를 설정합니다:
```
OPENAI_API_KEY=your_api_key_here
```

3. 서버 실행:
```bash
python run.py
```

## API 사용법

### 1. 모델 목록 조회
```bash
curl http://localhost:10000/models
```

### 2. 현재 사용 중인 모델 조회
```bash
curl "http://localhost:10000/model?client_name=your_client_name"
```

### 3. 모델 변경
```bash
curl -X POST http://localhost:10000/model \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4", "client_name": "your_client_name"}'
```

### 4. 대화 요청
```bash
curl -X POST http://localhost:10000/query \
  -H "Content-Type: application/json" \
  -d '{"input": "안녕하세요", "client_name": "your_client_name"}'
```

### 5. 대화 기록 조회
```bash
curl "http://localhost:10000/history?client_name=your_client_name"
```

### 6. 대화 기록 초기화
```bash
curl -X DELETE "http://localhost:10000/history?client_name=your_client_name"
```

## API 스키마

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "대화형 API 서버",
    "description": "OpenAI API를 활용한 대화형 REST API 서버",
    "version": "v1.0.0"
  },
  "servers": [
    {
      "url": "https://advanced-chat-server.onrender.com"
    }
  ],
  "paths": {
    "/models": {
      "get": {
        "operationId": "getModels",
        "summary": "사용 가능한 OpenAI 모델 목록 조회",
        "responses": {
          "200": {
            "description": "성공적인 응답",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "data": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "id": {
                            "type": "string",
                            "description": "모델 ID"
                          },
                          "object": {
                            "type": "string",
                            "description": "객체 타입"
                          },
                          "created": {
                            "type": "integer",
                            "description": "생성 시간 (Unix timestamp)"
                          },
                          "owned_by": {
                            "type": "string",
                            "description": "모델 소유자"
                          },
                          "permission": {
                            "type": "array",
                            "description": "모델 권한 정보 (없을 수 있음)",
                            "items": {
                              "type": "object"
                            },
                            "default": []
                          },
                          "root": {
                            "type": "string",
                            "description": "루트 모델 ID"
                          },
                          "parent": {
                            "type": "string",
                            "nullable": true,
                            "description": "부모 모델 ID (없을 수 있음)"
                          }
                        }
                      }
                    },
                    "object": {
                      "type": "string",
                      "description": "응답 객체 타입",
                      "example": "list"
                    }
                  }
                }
              }
            }
          },
          "500": {
            "description": "서버 에러",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "error": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/model": {
      "get": {
        "operationId": "getCurrentModel",
        "summary": "현재 사용 중인 모델 조회",
        "parameters": [
          {
            "name": "client_name",
            "in": "query",
            "required": true,
            "schema": {
              "type": "string",
              "description": "클라이언트 이름"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "성공적인 응답",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "model": {
                      "type": "string",
                      "description": "현재 사용 중인 모델 ID"
                    }
                  }
                }
              }
            }
          },
          "500": {
            "description": "서버 에러",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "error": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          }
        }
      },
      "post": {
        "operationId": "setModel",
        "summary": "사용할 모델 변경",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["model", "client_name"],
                "properties": {
                  "model": {
                    "type": "string",
                    "description": "변경할 모델 ID"
                  },
                  "client_name": {
                    "type": "string",
                    "description": "클라이언트 이름"
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "성공적인 응답",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "model": {
                      "type": "string",
                      "description": "변경된 모델 ID"
                    }
                  }
                }
              }
            }
          },
          "400": {
            "description": "잘못된 요청",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "error": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          },
          "500": {
            "description": "서버 에러",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "error": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/query": {
      "post": {
        "operationId": "query",
        "summary": "사용자 입력에 대한 응답 생성",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["input", "client_name"],
                "properties": {
                  "input": {
                    "type": "string",
                    "description": "사용자 입력 텍스트"
                  },
                  "client_name": {
                    "type": "string",
                    "description": "클라이언트 이름"
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "성공적인 응답",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "response": {
                      "type": "string",
                      "description": "OpenAI 응답 텍스트"
                    }
                  }
                }
              }
            }
          },
          "500": {
            "description": "서버 에러",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "error": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/history": {
      "get": {
        "operationId": "getHistory",
        "summary": "대화 기록 조회",
        "parameters": [
          {
            "name": "client_name",
            "in": "query",
            "required": true,
            "schema": {
              "type": "string",
              "description": "클라이언트 이름"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "성공적인 응답",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "role": {
                        "type": "string",
                        "enum": ["user", "assistant"]
                      },
                      "content": {
                        "type": "string"
                      },
                      "timestamp": {
                        "type": "string",
                        "format": "date-time"
                      }
                    }
                  }
                }
              }
            }
          },
          "500": {
            "description": "서버 에러",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "error": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          }
        }
      },
      "delete": {
        "operationId": "clearHistory",
        "summary": "대화 기록 초기화",
        "parameters": [
          {
            "name": "client_name",
            "in": "query",
            "required": true,
            "schema": {
              "type": "string",
              "description": "클라이언트 이름"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "성공적인 응답",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "message": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          },
          "500": {
            "description": "서버 에러",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "error": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
``` 