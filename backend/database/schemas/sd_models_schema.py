# schemas.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from database.models.enums import ResizeMode, ControlResizeMode, ControlMode,Gendre  # use the same enum classes

# Create a BaseSchema which sets the configuration to load data by attributes and to output
# enum values instead of full enum wrappers.
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

# Schemas for nested relationships

class SdModelVersionSchema(BaseSchema):
    id: int
    version_name: str

class SamplerModesSchema(BaseSchema):
    id: int
    name: str

class SamplerTypesSchema(BaseSchema):
    id: int
    name: str

class CategorySchema(BaseSchema):
    id: int
    name: str

class SdModelSchema(BaseSchema):
    id: int
    name: str
    description: Optional[str]
    sdmodel_version: SdModelVersionSchema

class TypeControlSchema(BaseSchema):
    id: int
    type_name: str
    description: Optional[str]
    preview_url: str
    sdmodel_versions: List[SdModelVersionSchema]


class ControlModelSchema(BaseSchema):
    id: int
    name: str
    description: Optional[str]
    type_control: TypeControlSchema

class ControlModuleSchema(BaseSchema):
    id: int
    name: str
    description: Optional[str]
    type_control: TypeControlSchema

class ControlNetSchema(BaseSchema):
    id: int
    name: str
    description: Optional[str]
    enabled: bool
    guidance_start: float
    guidance_end: float
    weight: float
    control_model: ControlModelSchema
    control_module: ControlModuleSchema
    control_mode: ControlMode              # Using the same SQLAlchemy enum
    resize_mode: ControlResizeMode         # Using the same SQLAlchemy enum


class ModelSchema(BaseSchema):
    id: int
    name: str
    description: Optional[str]
    active: bool
    preview_url: str
    type: Optional[str]
    prompt: Optional[str]
    negative_prompt: Optional[str]
    resize_mode: ResizeMode               # Using the same SQLAlchemy enum
    steps: Optional[int]
    save_images: Optional[bool]
    seed: Optional[int]
    width: Optional[int]
    height: Optional[int]
    cfg_scale: float
    gendre: Gendre

    sdmodel: SdModelSchema
    sampler_mode: SamplerModesSchema
    sampler_type: SamplerTypesSchema
    category: CategorySchema
    controlnets: List[ControlNetSchema]





class ControlNetArgPayload(BaseModel):
    enabled: bool
    model: str
    module: str
    image: dict
    guidance_start: float
    guidance_end: float
    weight: float
    control_mode: ControlMode         # Using the same enum from models.py
    resize_mode: ControlResizeMode    # Using the same enum from models.py
    pixel_perfect: bool

class ControlNetScriptPayload(BaseModel):
    args: List[ControlNetArgPayload]

class AlwaysOnScriptsPayload(BaseModel):
    ControlNet: ControlNetScriptPayload

class CreateModelPayload(BaseModel):
    model: str
    prompt: str
    negative_prompt: str
    resize_mode: ResizeMode           # Expects an integer value, e.g., 0
    steps: int
    save_images: bool
    seed: int
    width: int
    height: int
    cfg_scale: float
    sampler: str                      # The key is "sampler" (without a colon)
    alwayson_scripts: AlwaysOnScriptsPayload
    denoising_strength: float

    class Config:
        orm_mode = True