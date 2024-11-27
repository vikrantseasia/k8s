from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import endpoints


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(endpoints.router, prefix="/api/v1/deployments")
