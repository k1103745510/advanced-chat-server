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

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. `.env` 파일 생성:
- 프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:
```
OPENAI_API_KEY=your_api_key_here
```

3. 서버 실행:
```bash
python run.py
```

서버가 기본적으로 `http://localhost:10000`에서 실행됩니다.

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
    "/api-keys": {
      "post": {
        "operationId": "createApiKey",
        "summary": "새로운 API 키 생성",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["client_name"],
                "properties": {
                  "client_name": {
                    "type": "string",
                    "description": "클라이언트 이름"
                  },
                  "expires_in_days": {
                    "type": "integer",
                    "description": "만료 기간 (일)",
                    "nullable": true
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
                    "api_key": {
                      "type": "string",
                      "description": "생성된 API 키"
                    },
                    "client_name": {
                      "type": "string",
                      "description": "클라이언트 이름"
                    },
                    "created_at": {
                      "type": "string",
                      "format": "date-time",
                      "description": "생성 시간"
                    },
                    "expires_at": {
                      "type": "string",
                      "format": "date-time",
                      "description": "만료 시간",
                      "nullable": true
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
    "/api-keys/{api_key}": {
      "delete": {
        "operationId": "revokeApiKey",
        "summary": "API 키 비활성화",
        "parameters": [
          {
            "name": "api_key",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string"
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
          "404": {
            "description": "API 키를 찾을 수 없음",
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
    "/models": {
      "get": {
        "operationId": "getModels",
        "summary": "사용 가능한 OpenAI 모델 목록 조회",
        "security": [
          {
            "ApiKeyAuth": []
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
                            "items": {
                              "type": "object"
                            }
                          },
                          "root": {
                            "type": "string",
                            "description": "루트 모델 ID"
                          },
                          "parent": {
                            "type": "string",
                            "nullable": true,
                            "description": "부모 모델 ID"
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
          "401": {
            "description": "인증 실패",
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
    "/model": {
      "get": {
        "operationId": "getCurrentModel",
        "summary": "현재 사용 중인 모델 조회",
        "security": [
          {
            "ApiKeyAuth": []
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
          "401": {
            "description": "인증 실패",
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
      },
      "post": {
        "operationId": "setModel",
        "summary": "사용할 모델 변경",
        "security": [
          {
            "ApiKeyAuth": []
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["model"],
                "properties": {
                  "model": {
                    "type": "string",
                    "description": "변경할 모델 ID"
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
          "401": {
            "description": "인증 실패",
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
        "security": [
          {
            "ApiKeyAuth": []
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["input"],
                "properties": {
                  "input": {
                    "type": "string",
                    "description": "사용자 입력 텍스트"
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
          "401": {
            "description": "인증 실패",
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
    "/history": {
      "get": {
        "operationId": "getHistory",
        "summary": "대화 기록 조회",
        "security": [
          {
            "ApiKeyAuth": []
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
          "401": {
            "description": "인증 실패",
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
      },
      "delete": {
        "operationId": "clearHistory",
        "summary": "대화 기록 초기화",
        "security": [
          {
            "ApiKeyAuth": []
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
          "401": {
            "description": "인증 실패",
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
    }
  },
  "components": {
    "securitySchemes": {
      "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key"
      }
    }
  }
}
```

## API 사용 방법

### API 키 관리

#### POST /api-keys
새로운 API 키를 생성합니다.

**요청 형식:**
```json
{
    "client_name": "클라이언트 이름",
    "expires_in_days": 30  // 선택사항: 만료 기간 (일)
}
```

**응답 형식:**
```json
{
    "api_key": "생성된_API_키",
    "client_name": "클라이언트 이름",
    "created_at": "2024-03-21T10:30:00.000Z",
    "expires_at": "2024-04-20T10:30:00.000Z"  // 만료 기간이 설정된 경우
}
```

#### DELETE /api-keys/{api_key}
API 키를 비활성화합니다.

**응답 형식:**
```json
{
    "message": "API 키가 비활성화되었습니다."
}
```

### API 요청

모든 API 요청에는 `X-API-Key` 헤더가 필요합니다. 이 키는 각 클라이언트를 구분하는데 사용됩니다.

예시:
```bash
curl -X POST "https://advanced-chat-server.onrender.com/query" \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"input": "안녕하세요"}'
```

### GET /models

사용 가능한 OpenAI 모델 목록을 조회합니다.

**응답 형식:**
```json
{
    "data": [
        {
            "id": "gpt-4",
            "object": "model",
            "created": 1677610602,
            "owned_by": "openai",
            "permission": [...],
            "root": "gpt-4",
            "parent": null
        }
    ],
    "object": "list"
}
```

### GET /model

현재 사용 중인 모델을 조회합니다.

**응답 형식:**
```json
{
    "model": "gpt-3.5-turbo"
}
```

### POST /model

사용할 모델을 변경합니다.

**요청 형식:**
```json
{
    "model": "gpt-4"
}
```

**응답 형식:**
```json
{
    "model": "gpt-4"
}
```

**에러 응답 형식:**
```json
{
    "error": "사용할 수 없는 모델입니다. 사용 가능한 모델: gpt-3.5-turbo, gpt-4"
}
```

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