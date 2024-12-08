from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.routes.article_routes import router as article_router
from app.database import ArticleDB
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
db = ArticleDB()  # Initialize the database

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Cache-Control"]
)

# Include the article routes
app.include_router(article_router)

# Mount the frontend directory
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

# Mount the static directory for images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add root redirect to frontend
@app.get("/")
async def root():
    return RedirectResponse(url="/frontend/")

# Add error handling
@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal Server Error: {str(exc)}", exc_info=True)
    return {"detail": str(exc)}, 500

@app.on_event("startup")
async def startup_event():
    # Ensure the database is connected and tables are created
    db.create_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
