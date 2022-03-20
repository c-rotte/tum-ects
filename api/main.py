import functools
import os

import pymongo.errors

from database import Database
from fastapi import FastAPI, HTTPException
from typing import Optional

mongodb_connection = os.getenv("MONGODB", "mongodb://localhost:27017")

print("Connecting to MongoDB...")
database = Database(mongodb_connection)
if database.connection_error:
    print(f"Could not connect to <{mongodb_connection}>.")
    print(database.connection_error)
    exit(-1)

app = FastAPI()


@app.exception_handler(pymongo.errors.PyMongoError)
async def database_exception_handler(_, exc):
    print(exc)
    raise HTTPException(status_code=500, detail="internal database error")


@app.exception_handler(ValueError)
async def value_error_handler(_, exc):
    print(exc)
    raise HTTPException(status_code=500, detail="internal value error")


# request endpoints

@app.get("/")
async def read_status():
    return database.status()


@app.get("/degrees")
async def read_degrees():
    result = database.get_all_degree_ids()
    if not result:
        raise HTTPException(status_code=404, detail="no degrees found")
    return result


@app.get("/degree")
async def read_degree(degree_id: Optional[str] = None, list_modules: Optional[bool] = False):
    if not degree_id:
        raise HTTPException(status_code=400, detail="no degree_id provided")
    result = database.get_degree(degree_id.replace("_", " "), list_modules)
    if not result:
        raise HTTPException(status_code=404, detail="degree not found")
    return result


@app.get("/module")
async def read_module(degree_id: Optional[str] = None, module_id: Optional[str] = None):
    if not degree_id:
        raise HTTPException(status_code=400, detail="no degree_id provided")
    if not module_id:
        raise HTTPException(status_code=400, detail="no module_id provided")
    result = database.get_module(degree_id.replace("_", " "), module_id)
    if not result:
        raise HTTPException(status_code=404, detail="module not found")
    return result


@app.get("/parents")
async def read_parents(module_id: Optional[str] = None):
    if not module_id:
        raise HTTPException(status_code=400, detail="no module_id provided")
    result = database.get_degrees_with_module(module_id)
    if not result:
        raise HTTPException(status_code=404, detail="module not found")
    return result
