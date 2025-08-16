# agents-grocery: 에이전트 기반 FastAPI 서비스 템플릿

본 프로젝트는 LangChain/LangGraph 기반의 QA 에이전트를 포함한 FastAPI 서비스 템플릿입니다. 로깅, 안전한 HTTP 요청, 타이머/깊이 로깅 유틸리티, 설정 파일 기반 구성 등을 제공합니다.

## 0. 빠른 시작

- 의존성 및 테스트 환경 설치 (권장: conda)
  ```bash
  conda create -n agents-grocery python=3.12 -y
  conda activate agents-grocery
  pip install -r requirements.txt -r tests/requirements.txt
  ```
  - 주의: 일부 환경에서 `pip` 의존성 충돌이 발생할 수 있습니다. 충돌 시 버전을 완화하거나 업그레이드하여 재시도하세요.
- 테스트 실행
  ```bash
  pytest -q
  ```
- 애플리케이션 실행 (FastAPI)
  ```bash
  # 방법 1
  python -m app.main
  # 방법 2
  uvicorn app:application --host 0.0.0.0 --port 8000 --reload
  ```
  - 실행 후 브라우저에서 `http://localhost:8000/docs` 접속

## 1. 구성 및 환경

- **환경변수**

  - `ENV`: 서비스 실행 환경 (기본값: `dev`)
  - `SERVICE_NAME`: 서비스명 (기본값: `service_name`)
  - `SERVICE_VERSION`: 서비스 버전 (기본값: `service_version`)
  - `FASTAPI_ROOT_PATH`: 리버스 프록시 하위 경로가 있을 때 설정
  - OpenAI/Tavily 등 외부 API 키: `OPENAI_API_KEY`, `TAVILY_API_KEY` 등

- **설정 파일 경로** (`config/__init__.py` 기준)

  - `config/config.yaml`: 로컬 설정 파일 (존재 시 우선 적용)
  - `config/config.{ENV}.yaml`: `config.yaml`이 없을 경우, `{ENV}`에 맞는 설정 파일 사용
  - PostgreSQL DB: 로컬 설정 파일에 없는 항목에 대한 fallback으로 원격 DB 설정 사용

- **예시: `config/config.dev.yaml`** (발췌)

  ```yaml
  api:
    port: 8000
    workers: 1

  inference:
    llm:
      providers:
        openai_fast:
          model_config:
            model: gpt-4o-mini
            max_tokens: 8192
          max_concurrency: 16
        openai:
          model_config:
            model: gpt-5-mini
            max_tokens: 8192
            reasoning:
              effort: medium
              summary: null
            model_kwargs:
              text:
                verbosity: medium
          max_concurrency: 16
    embeddings:
      provider: local
      providers:
        local:
          model_config:
            openai_api_base: http://EMBEDDING_IP:58000/v1
            model: dragonkue/snowflake-arctic-embed-l-v2.0-ko
          dimensions: 1024
  ```

## 2. 실행 구조

- FastAPI 애플리케이션 엔트리포인트: `app:application`
  - 모듈 실행: `python -m app.main`
  - Uvicorn 실행: `uvicorn app:application --host 0.0.0.0 --port 8000 --reload`
- Lifespan(`app/__init__.py`)에서 에이전트 초기화/종료 훅을 관리합니다.
- 라우터는 다음과 같이 등록됩니다.
  - `GET /healthcheck`
  - `POST /chat/completions`

## 3. API 사용법

### 3.1 Healthcheck

- 경로: `GET /healthcheck`
- 응답 예시:
  ```json
  { "status": "success" }
  ```

### 3.2 Chat Completions

- 경로: `POST /chat/completions`
- 요청 바디 (`app/models/chat.py`):
  ```json
  {
    "query": "안녕하세요!",
    "user_id": "test"
  }
  ```
- 응답 바디:
  ```json
  {
    "success": true,
    "data": {
      "response": "네 반갑습니다!",
      "contexts": []
    }
  }
  ```
- 동작 방식: `src/agents/qa_agent.py`에서 LangChain/LangGraph 기반 에이전트가 웹 검색 리트리버(Tavily)와 임베딩 필터 등을 조합하여 답변과 컨텍스트를 생성합니다.

## 4. 코어 유틸리티 (`src/common/`)

### 4.1 Timer

- 컨텍스트 매니저

  ```python
  from time import sleep
  from src.common.timer import Timer

  with Timer("Task 1"):
      sleep(1)
  ```

- 데코레이터

  ```python
  from time import sleep
  from src.common.timer import Timer, T

  @Timer("Task 1")
  def fn1():
      sleep(1)

  @T
  def fn2():
      sleep(1)

  fn1()
  fn2()
  ```

### 4.2 Depth logging

```python
from src.common.depth_logging import D

@D
def main():
    main1()
    main2()

@D
def main1():
    main11()
    main12()

@D
def main11():
    return

@D
def main12():
    return

@D
def main2():
    main21()

@D
def main21():
    return

main()
```

### 4.3 Logging

- 콘솔 및 파일 로그를 지원합니다. 파일 로그는 `logs/YYYY-MM-DD.log`로 저장됩니다.
- 간단 사용 예:

  ```python
  from src.common.logger import (
      slog,
      log_info,
      log_success,
      log_error,
      log_warning,
      log_api,
      STYLES,
  )

  log_info("This is an info message.")
  log_success("This is a success message.")
  log_error("This is an error message.")
  log_warning("This is a warning message.")
  log_api("This is an API message.")
  for style in STYLES:
      slog(f"This is a {style} message.", style=style)
  ```

### 4.4 Safe HTTP requests

- 동기 방식:

  ```python
  from src.common.request_utils import safe_request

  url = "https://httpbin.org/post"
  payload = {"key": "value"}
  response = safe_request(url, json=payload, method="post")
  ```

- 비동기 방식:

  ```python
  import aiohttp
  from src.common.request_utils import async_safe_request

  async with aiohttp.ClientSession() as session:
      url = "https://httpbin.org/post"
      payload = {"key": "value"}
      response = await async_safe_request(session, url, json=payload, method="post")
  ```

## 5. 개발 환경

- **Dev Container**: `.devcontainer/devcontainer.json`
- **Docker**: `Dockerfile`, `docker-compose.yml`
- **Python**: `pyproject.toml`(설정), `requirements.txt`(의존성)

## 6. Playground

- 간단한 실행/시연 스크립트는 `playground/` 디렉터리에서 확인할 수 있습니다.
  - 예1: `playground/chore_add-tests-for-common-utils/verify_tests.py`
  - 예2: `playground/docs_update-readme/verify_readme_examples.py`

## 7. 자주 묻는 질문(FAQ)

- **OpenAI/Tavily 키는 어떻게 설정하나요?**
  - 다음 환경변수를 설정하세요: `export OPENAI_API_KEY=...`, `export TAVILY_API_KEY=...`
- **의존성 충돌이 발생합니다.**
  - `pip` 버전을 최신으로 업그레이드하고(`python -m pip install -U pip`), 문제가 되는 패키지 버전을 완화해 재시도하세요.

---

이 프로젝트가 여러분의 AI/에이전트 서비스 개발에 도움이 되기를 바랍니다!
