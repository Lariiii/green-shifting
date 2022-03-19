import logging
from typing import Optional
from fastapi import FastAPI, Form
from fastapi.datastructures import UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends, File

from minio_upload import minio_upload
from dependencies import execute_query, get_sqlalch_session, WorkspaceValidation
from models import PlatformSettings, Plant
from routers.cycle import cycleRouter
from routers.edge import edgeRouter
from routers.incident import incidentRouter
from routers.license import licenseRouter, license_valid
from routers.machine import machineRouter
from routers.statistics import statisticsRouter
from routers.user import userRouter, User, get_current_user
from routers.workspace import workspaceRouter

# API Code
app = FastAPI()
debug = False

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.post('/do-it')
def create_plant(test: str):
    return test