# TechPressure

AI-powered IT interview simulator with two phases (Interview Round + Coding Challenge), live scoring, TTS, and STT.

## Structure

```
techpressure/
├── frontend/     ← React web app (port 3000)
└── backend/      ← Flask API server (port 5000)
```

## Run both

```bash
# Terminal 1 — backend
cd backend
pip install -r requirements.txt
python app.py

# Terminal 2 — frontend
cd frontend
npm install
npm start
```

