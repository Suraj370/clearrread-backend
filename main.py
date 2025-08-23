from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from config import FRONTEND_URL

app = FastAPI(title="Dyslexia-Friendly Text Converter API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Dyslexia-Friendly Text Converter API is running"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)