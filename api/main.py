import functools
import os

import pymongo.errors

from database import Database
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
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
    """default exception handler for database errors"""
    print(exc)
    return JSONResponse(
        status_code=500,
        content={"error": "internal database error"}
    )


@app.exception_handler(ValueError)
async def value_error_handler(_, exc):
    """default exception handler for value errors"""
    print(exc)
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )


# request endpoints

@app.get("/")
async def read_status():
    return database.status()


@app.get("/pStpStpNrs")
async def read_pStpStpNrs(language: Optional[str] = "english"):
    result = database.get_all_pStpStpNrs(language)
    if not result:
        raise HTTPException(status_code=404, detail="no pStpStpNrs found")
    return result


@app.get("/curriculum")
async def read_curriculum(pStpStpNr: Optional[int] = None, language: Optional[str] = "english"):
    if not pStpStpNr:
        raise HTTPException(status_code=400, detail="no pStpStpNr provided")
    result = database.get_curriculum(pStpStpNr, language)
    if not result:
        raise HTTPException(status_code=404, detail="curriculum not found")
    return result


@app.get("/modules")
async def read_modules(pStpStpNr: Optional[int] = None, language: Optional[str] = "english"):
    if not pStpStpNr:
        raise HTTPException(status_code=400, detail="no pStpStpNr provided")
    result = database.get_modules(pStpStpNr, language)
    if not result:
        raise HTTPException(status_code=404, detail="curriculum not found")
    return result


@app.get("/module")
async def read_module(pStpStpNr: Optional[int] = None,
                      module_id: Optional[str] = None,
                      language: Optional[str] = "english"):
    if not pStpStpNr:
        raise HTTPException(status_code=400, detail="no pStpStpNr provided")
    if not module_id:
        raise HTTPException(status_code=400, detail="no module_id provided")
    result = database.get_module(pStpStpNr, module_id, language)
    if not result:
        raise HTTPException(status_code=404, detail="module not found")
    return result


@app.get("/parents")
async def read_parents(module_id: Optional[str] = None, language: Optional[str] = "english"):
    if not module_id:
        raise HTTPException(status_code=400, detail="no module_id provided")
    result = database.get_pStpStpNrs_with_module(module_id, language)
    if not result:
        raise HTTPException(status_code=404, detail="module not found")
    return result


@app.get("/degrees")
async def read_degrees(degree_id: Optional[str] = None, language: Optional[str] = "english"):
    if not degree_id:
        raise HTTPException(status_code=400, detail="no degree_id provided")
    result = database.get_pStpStpNrs_with_degree(degree_id=degree_id.replace("_", " "), language=language)
    if not result:
        raise HTTPException(status_code=404, detail="degree not found")
    return result
