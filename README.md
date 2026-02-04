# Somm.dev

Next.js 16 + Python(FastAPI) 풀스택 프로젝트

## 프로젝트 구조

```
somm.dev/
├── frontend/          # Next.js 16 + TypeScript + Tailwind CSS
├── backend/           # Python FastAPI
└── README.md
```

## 시작하기

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```
- 개발 서버: http://localhost:3000

### Backend (Python)

```bash
cd backend

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py
```
- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 기술 스택

### Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- ESLint

### Backend
- Python 3.12+ (3.14 ready)
- FastAPI
- Uvicorn
- Pydantic

## API 엔드포인트

- `GET /` - Health check
- `GET /health` - Health check
- `POST /api/echo` - Echo test endpoint

## 라이선스

MIT
