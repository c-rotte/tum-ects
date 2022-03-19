import os
from database import Database
from fastapi import FastAPI
from typing import Optional

mongodb_connection = os.getenv("MONGODB", "mongodb://localhost:27017")

print("Connecting to MongoDB...")
database = Database(mongodb_connection)
if database.connection_error:
    print(f"Could not connect to <{mongodb_connection}>.")
    print(database.connection_error)
    exit(-1)

app = FastAPI()


@app.get("/")
async def read_status():
    try:
        return database.status()
    except Exception as e:
        print(e)
        return {"error": "invalid database response"}


@app.get("/module")
async def read_module(degree_id: Optional[str] = None, module_id: Optional[str] = None):
    if not degree_id:
        return {
            "error": "no degree_id provided"
        }
    if not module_id:
        return {
            "error": "no module_id provided"
        }
    try:
        result = database.get_module(degree_id.replace("_", " "), module_id)
        if not result:
            return {}
        return result
    except Exception as e:
        print(e)
        return {"error": "invalid database response"}
