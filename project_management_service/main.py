from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from app.endpoints import getprojects, getsidebar, addprojects, updateprojects, deleteproject
from utils.celery import Celery

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = exc.errors()
    detailed_errors = []
    for error in errors:
        field = ".".join(map(str, error['loc']))
        message = f"Error in field '{field}': {error['msg']}"
        detailed_errors.append(message)

    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": detailed_errors}
    )

# Include routers
app.include_router(getprojects.router, prefix="/api/v1/projects")
app.include_router(addprojects.router, prefix="/api/v1/projects")
app.include_router(updateprojects.router, prefix="/api/v1/projects")
app.include_router(deleteproject.router, prefix="/api/v1/projects")
app.include_router(getsidebar.router, prefix="/api/v1/sidebar")

celery_app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
