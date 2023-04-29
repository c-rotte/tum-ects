from peewee import DoesNotExist
from fastapi import FastAPI, HTTPException
from typing import Optional

from database.database import init_db, Module, Degree, Mapping

app = FastAPI()

print("Connecting to database... ")
init_db()

@app.get("/")
def get_counts():
    return {
        "number_of_degrees": Degree.select().count(),
        "number_of_modules": Module.select().count(),
        "number_of_mappings": Mapping.select().count()
    }


@app.get("/degree")
def get_degree(degree_id: int):
    try:
        return Degree.get_by_id(degree_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Degree not found")

@app.get("/degrees")
def get_degrees():
    return list(Degree.select())


@app.get("/module")
def get_module(module_id: int):
    try:
        return Module.get_by_id(module_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Module not found")

@app.get("/modules_of_degree")
def get_modules_of_degree(degree_id: int, valid_from: Optional[str] = None, valid_to: Optional[str] = None,
                          degree_version: Optional[str] = None):
    modules = get_modules_of_degree(degree_id, valid_from, valid_to, degree_version)
    if not modules:
        raise HTTPException(status_code=404, detail="No modules found for the given degree")
    return list(modules)