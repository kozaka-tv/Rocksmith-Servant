import configparser
import os

from app.routers.config import config as config
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Allow requests from Angular frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers (e.g., Authorization, Content-Type)
)

# Include a router for your REST endpoints
app.include_router(config)

# Constants
CONFIG_FILE_PATH = "../../../config.ini"


# Helper: Read config.ini file
def read_config():
    print("in read_config")
    if not os.path.exists(CONFIG_FILE_PATH):
        raise HTTPException(status_code=404, detail="Config file not found!")
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return {section: dict(config.items(section)) for section in config.sections()}


# Helper: Write to config.ini file
def write_config(updated_config: dict):
    print("in write_config")
    config = configparser.ConfigParser()
    for section, values in updated_config.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, value in values.items():
            config.set(section, key, str(value))
    with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as config_file:
        config.write(config_file)


# Pydantic Model for Input Validation
class ConfigUpdate(BaseModel):
    print("in ConfigUpdate")
    config: dict


# Route to fetch the current configuration
@app.get("/api/config")
def get_config():
    print("in get_config")
    try:
        config_data = read_config()
        return {"config": config_data}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}") from e


# Route to update the configuration
@app.post("/api/config")
def update_config(update: ConfigUpdate):
    print("in update_config")
    try:
        write_config(update.config)
        return {"message": "Configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}") from e


@app.get("/")
def read_root():
    return {"message": "Welcome to config service!"}


