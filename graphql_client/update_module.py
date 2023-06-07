# Generated by ariadne-codegen on 2023-06-07 16:48
# Source: schema/queries.graphql

from typing import Optional

from pydantic import Field

from .base_model import BaseModel


class UpdateModule(BaseModel):
    update_module: Optional["UpdateModuleUpdateModule"] = Field(alias="updateModule")


class UpdateModuleUpdateModule(BaseModel):
    id: str
    number: str


UpdateModule.update_forward_refs()
UpdateModuleUpdateModule.update_forward_refs()
