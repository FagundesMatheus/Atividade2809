from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import files, tags, categories
from .dependencies import get_app_directory
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "http://localhost:5173",  # Default Vite dev server port
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(files.router, prefix="/files", tags=["files"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.mount("/images", StaticFiles(directory=str(get_app_directory() / "images")), name="images")
