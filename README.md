# 📄 AI Document Insight Tool  

An **AI-powered resume analyzer** that lets you upload PDF resumes and instantly get concise summaries or fallback insights.  
Built with **FastAPI + Sarvam AI + SQLite + Docker + Render**.  

---

## 🚀 Features  
- ✅ Upload PDF resumes  
- ✅ Extract text & generate AI summary (Sarvam AI)  
- ✅ Fallback: top 5 frequent words if AI fails  
- ✅ History tab → view all past uploads  
- ✅ Frontend + Backend served together  
- ✅ Dockerized → easy deployment  
- ✅ Live on **Render**  

---

## 🏗️ Tech Stack  
- **Backend:** FastAPI (Python), Uvicorn  
- **AI API:** Sarvam AI (summarization)  
- **Database:** SQLite (SQLAlchemy ORM)  
- **Frontend:** HTML, CSS, JavaScript  
- **Deployment:** Docker + Render  

---

## 📂 Project Structure  
ai-document-insight-tool/
│
├── server/ # FastAPI backend
│ ├── main.py # API endpoints
│ ├── models.py # SQLite models
│ └── .env # Sarvam API key (not committed)
│
├── frontend/ # Frontend UI
│ ├── index.html
│ ├── style.css
│ └── script.js
│
├── Dockerfile # Docker build config
├── docker-compose.yml # Docker Compose config
├── requirements.txt # Python dependencies
└── README.md # Documentation

