# Inflo View

Streamlit을 기반으로 한 데이터 시각화 및 대시보드 애플리케이션입니다.

## 개요

Inflo View는 수집된 데이터를 시각적으로 표현하고 분석할 수 있는 웹 기반 대시보드입니다. Streamlit을 사용하여 인터랙티브한 데이터 시각화와 분석 도구를 제공합니다.

## 주요 기능

- **인터랙티브 대시보드**: Streamlit 기반의 사용자 친화적 인터페이스
- **데이터 시각화**: 다양한 차트와 그래프를 통한 데이터 표현
- **실시간 데이터 표시**: 최신 데이터의 실시간 업데이트
- **필터링 및 검색**: 데이터 필터링 및 검색 기능
- **반응형 디자인**: 다양한 화면 크기에 최적화된 레이아웃

## 기술 스택

- **Python 3.12**
- **Streamlit**: 웹 애플리케이션 프레임워크
- **Streamlit Extras**: 추가 UI 컴포넌트
- **FastAPI**: 백엔드 API (필요시)
- **AIOHTTP**: 비동기 HTTP 클라이언트
- **PyYAML**: 설정 파일 관리

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 설정

`config/` 디렉토리에서 필요한 설정 파일을 구성하세요.

### 3. 애플리케이션 실행

```bash
streamlit run app/main.py
```

또는

```bash
python -m streamlit run app/main.py
```

### 4. 웹 브라우저 접속

브라우저에서 `http://localhost:8501`에 접속하여 애플리케이션을 확인할 수 있습니다.

## 프로젝트 구조

```
inflo-view/
├── app/                  # Streamlit 애플리케이션
├── src/                  # 소스 코드
├── config/               # 설정 파일
├── tests/                # 테스트 코드
├── logs/                 # 로그 파일
├── docker/               # Docker 설정
├── experiment/           # 실험용 코드
└── .devcontainer/        # 개발 컨테이너 설정
```

## 주요 페이지

### 대시보드
- 전체 시스템 현황 개요
- 주요 지표 및 통계

### 데이터 분석
- 수집된 데이터의 상세 분석
- 다양한 차트 및 그래프

### 설정
- 시스템 설정 및 구성
- 사용자 환경 설정

## 개발 환경

### 로컬 개발

1. Python 3.12+ 설치
2. 가상환경 생성 및 활성화
3. 의존성 설치
4. Streamlit 애플리케이션 실행

### Docker 개발

```bash
docker-compose up -d
```

## 설정

### 환경 변수

필요한 환경 변수를 설정하거나 `config/` 디렉토리의 설정 파일을 사용하세요.

### 데이터베이스 연결

다른 Inflo 모듈들과의 데이터베이스 연결 설정을 확인하세요.

## 커스터마이징

### 새로운 페이지 추가

1. `app/` 디렉토리에 새로운 Python 파일 생성
2. Streamlit 위젯을 사용하여 페이지 구성
3. 메인 네비게이션에 페이지 추가

### 테마 변경

Streamlit의 테마 설정을 통해 UI를 커스터마이징할 수 있습니다.

## 배포

### 로컬 배포

```bash
streamlit run app/main.py --server.port 8501
```

### Docker 배포

```bash
docker build -t inflo-view .
docker run -p 8501:8501 inflo-view
```

## 문제 해결

### 일반적인 문제

1. **포트 충돌**: 다른 포트로 변경하여 실행
2. **의존성 오류**: 가상환경 재생성 및 의존성 재설치
3. **데이터 연결 오류**: 데이터베이스 연결 설정 확인

## 라이선스

프로젝트 라이선스 정보를 여기에 추가하세요.
