import os
from pprint import pprint

from fastapi import FastAPI, HTTPException
from typing import Optional

from database.tumread import TUMReadDatabase

app = FastAPI()

database = TUMReadDatabase()

@app.get("/")
def get_counts():
    return {
        "number_of_degrees": database.get_number_of_degrees(),
        "number_of_modules": database.get_number_of_modules(),
        "number_of_mappings": database.get_number_of_mappings()
    }


@app.get("/degree")
def get_degree(degree_id: int):
    degree_info = database.get_degree_info(degree_id)
    if not degree_info:
        raise HTTPException(status_code=404, detail="Degree not found")
    return degree_info


@app.get("/degrees")
def get_degrees():
    return list(database.get_all_degrees())


@app.get("/module")
def get_module(module_id: int):
    module_info = database.get_module_info(module_id)
    if not module_info:
        raise HTTPException(status_code=404, detail="Module not found")
    return module_info

@app.get("/modules_of_degree")
def get_modules_of_degree(degree_id: int, valid_from: Optional[str] = None, valid_to: Optional[str] = None,
                          degree_version: Optional[str] = None):
    modules = database.get_modules_of_degree(degree_id, valid_from, valid_to, degree_version)
    if not modules:
        raise HTTPException(status_code=404, detail="No modules found for the given degree")
    return list(modules)