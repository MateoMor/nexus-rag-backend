from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.api import api_router
from src.core.config import settings
from src.utils.logger import setup_logging

# Setup logging
setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="RAG application with LlamaIndex and FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )