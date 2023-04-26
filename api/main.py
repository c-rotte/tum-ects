import os

from fastapi import FastAPI, HTTPException
from typing import Optional
from database import TUMReadDatabase

app = FastAPI()
database = TUMReadDatabase(
    name="postgres",
    host="database",
    user="postgres",
    password="postgres",
    port=int(os.getenv("DATABASE_PORT", 5432))
)


@app.get("/")
def get_counts():
    return {
        "number_of_degrees": database.get_number_of_degrees(),
        "number_of_modules": database.get_number_of_modules(),
    }


@app.get("/degree")
def get_degree(degree_id: int):
    degree_info = database.get_degree_info(degree_id)
    if not degree_info:
        raise HTTPException(status_code=404, detail="Degree not found")
    return {
        "degree_id": degree_info[0],
        "full_text_en": degree_info[1],
        "short_text_en": degree_info[2],
        "full_text_de": degree_info[3],
        "short_text_de": degree_info[4],
    }


@app.get("/degrees")
def get_degrees():
    degrees = database.get_all_degrees()
    return [
        {
            "degree_id": degree[0],
            "full_text_en": degree[1],
            "short_text_en": degree[2],
            "full_text_de": degree[3],
            "short_text_de": degree[4],
        }
        for degree in degrees
    ]


@app.get("/module")
def get_module(module_id: int):
    module_info = database.get_module_info(module_id)
    if not module_info:
        raise HTTPException(status_code=404, detail="Module not found")
    return {
        "module_id": module_info[0],
        "name_en": module_info[1],
        "name_de": module_info[2],
    }


@app.get("/modules_of_degree")
def get_modules_of_degree(degree_id: int, valid_from: Optional[str] = None, valid_to: Optional[str] = None,
                          degree_version: Optional[str] = None):
    modules = database.get_modules_of_degree(degree_id, valid_from, valid_to, degree_version)
    if not modules:
        raise HTTPException(status_code=404, detail="No modules found for the given degree")
    return [{
        "module_id": m[0],
        "name_en": m[1],
        "name_de": m[2]
    } for m in modules]
