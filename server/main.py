from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pdfminer.high_level import extract_text
import tempfile
import os
from dotenv import load_dotenv
import httpx
from collections import Counter
import re
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

# ---------- Setup ----------
load_dotenv()
SARVAM_API_KEY = os.getenv("SARAMV_API_KEY")

print("DEBUG - Loaded Sarvam API Key:", SARVAM_API_KEY)

app = FastAPI()

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

# --- Frontend static serving ---
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = (BASE_DIR / ".." / "frontend").resolve()

# Serve everything in /frontend at /static/*
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# Serve index.html at root
@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


# ---------- Enable CORS (important for frontend) ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 allow all for now (later you can restrict to frontend URL)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Database Setup ----------
DATABASE_URL = "sqlite+aiosqlite:///./history.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ---------- Routes ----------
@app.get("/")
def home():
    return {"message": "AI Document Insight Tool backend is running!"}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    # Save PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    # Extract text
    try:
        text = extract_text(tmp_path)
    except Exception as e:
        return JSONResponse({"error": f"Failed to extract text: {str(e)}"}, status_code=500)

    summary = None
    try:
        headers = {
            "API-Subscription-Key": SARVAM_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sarvam-m",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Summarize resumes into concise bullet points under 120 words."},
                {"role": "user", "content": text[:6000]}
            ],
            "temperature": 0.2
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.sarvam.ai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

        print("DEBUG - Sarvam response code:", response.status_code)
        print("DEBUG - Sarvam response body:", response.text)

        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if choices and "message" in choices[0]:
                summary = choices[0]["message"].get("content", "").strip()
    except Exception as e:
        print("Sarvam AI failed:", e)

    # Fallback if AI fails
    if not summary:
        words = re.findall(r'\w+', text.lower())
        common = Counter(words).most_common(5)
        summary = f"Top 5 frequent words: {', '.join([w for w, _ in common])}"

    # ---------- Save to DB ----------
    async with AsyncSessionLocal() as session:
        new_record = History(filename=file.filename, summary=summary)
        session.add(new_record)
        await session.commit()

    return JSONResponse({
        "filename": file.filename,
        "summary": summary
    })

@app.get("/insights")
async def get_insights():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            History.__table__.select().order_by(History.timestamp.desc())
        )
        rows = result.fetchall()

    history_list = [
        {
            "id": row.id,
            "filename": row.filename,
            "summary": row.summary,
            "timestamp": row.timestamp.isoformat()
        }
        for row in rows
    ]

    return history_list
