# app/main.py
from fastapi import FastAPI, Request, status # Add Request, status
from fastapi.responses import JSONResponse # Add JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager # For lifespan manager

from app.core.config import settings
from app.db.session import engine # Assuming engine is exposed from session.py
from app.models.base import Base # To create tables
from app.api.v1.endpoints import auth as api_auth # Router for auth
from app.api.v1.endpoints import characters as api_characters # Router for characters
from app.api.v1.endpoints import game as api_game # Router for game
from app.core.rag_system import RAGSystem
from app.core.plugin_system import PluginManager
# Import custom exceptions if defined and to be handled globally
# from app.utils.exceptions import GameException, NotFoundError, ValidationError

# Lifespan manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    print("Application startup...")

    # 1. Create database tables (for MVP, use create_all. Production should use Alembic)
    print("Initializing database...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully (if they didn't exist).")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        # Depending on severity, you might want to prevent app startup

    # 2. Initialize RAG System
    print("Initializing RAG System...")
    try:
        rag_system_instance = RAGSystem()
        app.state.rag_system = rag_system_instance
        print("RAG System initialized successfully.")
    except Exception as e:
        print(f"Error initializing RAG System: {e}")
        app.state.rag_system = None # Ensure it's None if init fails
        # Consider if app should start if RAG fails

    # 3. Initialize Plugin Manager and load plugins
    print("Initializing Plugin Manager and loading plugins...")
    try:
        # Ensure 'plugins' dir is relative to the project root.
        # If main.py is in app/, plugins_dir should be "../plugins" if PluginManager expects it relative to its own location
        # or an absolute path. Given PluginManager defaults to "plugins", it assumes project root.
        plugin_manager_instance = PluginManager(plugins_dir="plugins")
        plugin_manager_instance.load_plugins()
        app.state.plugin_manager = plugin_manager_instance
        print("Plugin Manager initialized and plugins loaded successfully.")
    except Exception as e:
        print(f"Error initializing Plugin Manager or loading plugins: {e}")
        app.state.plugin_manager = None # Ensure it's None if init fails

    yield # Application runs here

    # --- Shutdown ---
    print("Application shutdown...")
    if hasattr(app.state, 'plugin_manager') and app.state.plugin_manager:
        print("Unloading plugins...")
        try:
            app.state.plugin_manager.unload_plugins()
            print("Plugins unloaded successfully.")
        except Exception as e:
            print(f"Error unloading plugins: {e}")
    # Other cleanup tasks can go here (e.g., closing DB connections if not handled by SQLAlchemy engine)

# Create FastAPI app instance with lifespan manager
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# --- Middleware ---
# CORS Middleware (adjust origins as needed for your frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins for MVP development
    # allow_origins=["http://localhost", "http://localhost:3000"], # Example for specific origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# --- Global Exception Handlers (Optional for MVP, but good practice) ---
# Example: Catching all other exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled exception: {exc} (Path: {request.url.path})") # Log the full error and path
    # In production, avoid sending detailed error like str(exc) to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected internal server error occurred.",
            "data": None # Ensure data is None or omitted for BaseResponse consistency
        },
    )

# Example: Handling a custom GameException
# @app.exception_handler(GameException)
# async def game_exception_handler(request: Request, exc: GameException):
#     return JSONResponse(
#         status_code=exc.error_code, # Use error code from custom exception
#         content={
#             "success": False,
#             "message": exc.message,
#             "data": None
#         },
#     )

# --- API Routers ---
# Mount the API routers with a prefix
app.include_router(api_auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(api_characters.router, prefix=f"{settings.API_V1_STR}/characters", tags=["Characters"])
app.include_router(api_game.router, prefix=f"{settings.API_V1_STR}/game", tags=["Game"])


# --- Root endpoint (optional) ---
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API. Docs at /docs or /redoc."}

# For Uvicorn to run this app (if running `uvicorn app.main:app`):
# The file is `app/main.py`, so the command `uvicorn app.main:app --reload` from the project root should work.
