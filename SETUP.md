# Setup Guide

Complete setup instructions for somm.dev development and deployment.

## Prerequisites

- Python 3.12+
- Node.js 20+
- MongoDB (local or Atlas)
- GitHub account with CLI access

## 1. Clone Repository

```bash
git clone https://github.com/Two-Weeks-Team/somm.dev.git
cd somm.dev
```

## 2. Backend Setup

### 2.1 Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.3 Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your actual values
```

**Required variables:**
- `MONGODB_URI`: MongoDB connection string
- `VERTEX_API_KEY`: Vertex AI Express API key
- `GITHUB_TOKEN`: Generate at https://github.com/settings/tokens (needs `repo` scope)

### 2.4 Run Backend

```bash
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

## 3. Frontend Setup

### 3.1 Install Dependencies

```bash
cd frontend
npm install
```

### 3.2 Configure Environment Variables

```bash
cp .env.example .env.local
# Default values should work for local development
```

### 3.3 Run Frontend

```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## 4. GitHub Secrets (for CI/CD)

Set these secrets in your GitHub repository (Settings → Secrets → Actions):

| Secret | Description | How to Get |
|--------|-------------|------------|
| `VERTEX_API_KEY` | Vertex AI Express API key | Google Cloud Console |
| `GITHUB_TOKEN` | GitHub PAT | https://github.com/settings/tokens |
| `FLY_API_TOKEN` | Fly.io token | `flyctl auth token` |
| `VERCEL_TOKEN` | Vercel token | https://vercel.com/account/tokens |

Set via CLI:
```bash
gh secret set VERTEX_API_KEY
gh secret set GITHUB_TOKEN
```

## 5. MongoDB Setup

### Option A: Local MongoDB

```bash
# macOS with Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Default URI
MONGODB_URI=mongodb://localhost:27017/somm_db
```

### Option B: MongoDB Atlas (Cloud)

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a new cluster
3. Add your IP to the whitelist
4. Create a database user
5. Get connection string

```bash
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/somm_db
```

## 6. API Keys

### Vertex AI Express API Key

1. Go to Google Cloud Console
2. Enable Vertex AI API
3. Create API key for Vertex AI Express
4. Copy to `backend/.env` as `VERTEX_API_KEY`

### GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo` (full control of private repositories)
4. Copy to `backend/.env`

## 7. Development Workflow

1. Start MongoDB: `brew services start mongodb-community` (if using local)
2. Start backend: `cd backend && source venv/bin/activate && uvicorn main:app --reload`
3. Start frontend: `cd frontend && npm run dev`
4. Open http://localhost:3000

## 8. Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 9. Deployment

### Backend (Fly.io)

```bash
cd backend
flyctl deploy
```

### Frontend (Vercel)

```bash
cd frontend
vercel --prod
```

Or push to main branch for automatic deployment via GitHub Actions.

## Troubleshooting

### Port already in use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### MongoDB connection issues

```bash
# Check MongoDB status
brew services list | grep mongodb

# Restart MongoDB
brew services restart mongodb-community
```

### Module not found errors

```bash
# Reinstall backend dependencies
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Reinstall frontend dependencies
rm -rf node_modules package-lock.json
npm install
```

## Support

For issues or questions:
- Check existing issues: https://github.com/Two-Weeks-Team/somm.dev/issues
- Create new issue with detailed description
