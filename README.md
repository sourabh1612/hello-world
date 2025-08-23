# Watercolor Face Swap MVP

## Dev
- Backend
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```
- Frontend
```bash
cd frontend
npm install
npm run dev
```

## Build (production)
```bash
# frontend
cd frontend && npm run build
# serve built frontend via FastAPI static files by copying dist to backend/frontend/dist
mkdir -p backend/frontend
cp -r frontend/dist backend/frontend/
# backend
source venv/bin/activate
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```
