from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.ask import router as ask_router
from app.api.conversations import router as conversations_router
from app.api.auth import router as auth_router
from app.api.comparison import router as comparison_router


app = FastAPI(
    title="Enterprise RAG Assistant",
    description="Intelligent Enterprise Knowledge & Decision Assistant",
    version="1.0.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Routers
# --------------------------------------------------

app.include_router(documents_router)
app.include_router(search_router)
app.include_router(ask_router)
app.include_router(conversations_router)
app.include_router(auth_router)
app.include_router(comparison_router)


# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Enterprise RAG Assistant API is running"
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "Enterprise RAG Assistant"
    }