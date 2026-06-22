from unicodedata import category
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from core.database import get_db
from database.models import SdModelVersion, SdModel, TypeControl, ControlModel, ControlModule, ControlNet, SamplerModeTable, SamplerTypeTable, ModelCategoryTable, Model, sdmodelversion_typecontrol_association, model_controlnet_association
from database.models.enums import ControlMode, ControlResizeMode, ResizeMode, Gendre
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime
from sqlalchemy import select
from database.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional, Set
from fastapi.responses import JSONResponse
from database.models.enums import UserRole
from api.v1.auth.dependencies import get_current_user, verify_org_access, get_current_admin
from fastapi import Query
from sqlalchemy.orm import joinedload  # Add this import at the top
import logging
from fastapi import Request, APIRouter, HTTPException
logger = logging.getLogger("foo")          # Creating a logger instance
print("Debug log: Starting database initialization")
print("hello")

router = APIRouter(
    prefix="/models",
    tags=["models"]
)

class TypeControlCreate(BaseModel):
    type_name: str
    description: Optional[str] = None
    preview_image: str
    associated_versions: List[int] = []  # Assuming these are IDs of SdModelVersions

class SdModelVersionTypeControlAssociation(BaseModel):
    sdmodelversion_id: int
    typecontrol_id: int

class SdModelVersionResponse(BaseModel):
    id: int
    version_name: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class TypeControlBase(BaseModel):
    name: str = Field(alias='type_name')
    description: Optional[str] = None
    preview_url: str
    associated_versions: List[SdModelVersionResponse] = []

    class Config:
        from_attributes = True
        populate_by_name = True  # Allows both name and type_name to work


class TypeControlResponse(TypeControlBase):
    id: int

    class Config:
        from_attributes = True
        orm_mode = True

class TypeControlNewCreate(BaseModel):
    type_name: str
    description: Optional[str] = None
    preview_image: str
    associated_versions: List[int] = []  # Assuming these are IDs of SdModelVersions

    class Config:
        orm_mode = True


class TypeControlCreateResponse(TypeControlNewCreate):
    id: int
    preview_image: str

    class Config:
        from_attributes = True
        orm_mode = True


class ModelCategoryBase(BaseModel):
    name: str


class ModelCategoryResponse(ModelCategoryBase):
    id: int
    name: str
    
    class Config:
        from_attributes = True

# Pydantic models for request/response


class SdModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    sdmodel_version_id: int



class SdModelCreate(SdModelBase):
    pass


class SdModelResponse(SdModelBase):
    id: int
    created_at: datetime
    name: str
    sdmodel_version: SdModelVersionResponse


    class Config:
        from_attributes = True
        

class ControlModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    typecontrol_id: int

class ControlModelCreate(ControlModelBase):
    pass


class ControlModelResponse(ControlModelBase):
    id: int
    created_at: datetime
    type_control: TypeControlResponse

    class Config:
        from_attributes = True


class ControlModuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    typecontrol_id: int

class ControlModuleCreate(ControlModuleBase):
    pass


class ControlModuleResponse(ControlModuleBase):
    id: int
    created_at: datetime
    type_control: TypeControlResponse

    class Config:
        from_attributes = True


class SamplerModeBase(BaseModel):
    name: str


class SamplerModeCreate(SamplerModeBase):
    pass


class SamplerModeResponse(SamplerModeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SamplerTypeBase(BaseModel):
    name: str


class SamplerTypeResponse(SamplerTypeBase):
    id: int

    class Config:
        from_attributes = True


class ControlNetBase(BaseModel):
    name: str
    description: Optional[str] = None
    enabled: bool = False
    guidance_start: float = 0.0
    guidance_end: float = 1.0
    weight: float = 1.0
    control_mode: ControlMode = ControlMode.BALANCED
    resize_mode: ControlResizeMode = ControlResizeMode.JUSTRESIZE
    control_model_id: int
    control_module_id: int

    class Config:
        from_attributes = True
        orm_mode = True


class ControlNetCreate(ControlNetBase):
    pass


class ControlNetResponse(ControlNetBase):
    id: int
    control_model: ControlModelResponse
    control_module: ControlModuleResponse
    created_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True

class ControlNetResponseFiltered(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True
        orm_mode = True
    
class ModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool = True
    preview_url: str
    type: Optional[str] = None
    sdmodel_id: Optional[int] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    resize_mode: ResizeMode = ResizeMode.JUSTRESIZE
    gendre:Gendre=Gendre.MEN
    steps: Optional[int] = None
    save_images: Optional[bool] = None
    seed: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    cfg_scale: float = 7.0
    sampler_mode_id: int
    sampler_type_id: int
    

    class Config:
        orm_mode =True

    



class ModelCreate(ModelBase):
    preview_image:str
    listcontrolnets: List[int] = []
    categorie_id: int = None


    


class ModelBaseResponse(ModelBase):
    id: int
    created_at: datetime


    class Config:
        from_attributes = True
        


class ModelResponse(ModelBase):
    id: int
    sdmodel: SdModelResponse
    sampler_mode: SamplerModeResponse
    sampler_type: SamplerTypeResponse
    category: ModelCategoryResponse
    controlnets: List["ControlNetResponse"] = []
    created_at: datetime
    resize_mode_name: str
    gendre: Gendre

    class Config:
        from_attributes = True
        orm_mode =True


class ModelListResponse(ModelBase):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    



class SdModelVersionBase(BaseModel):
    version_name: str






@router.post("/type-controls", response_model=TypeControlCreateResponse)
async def create_type_control(
    model: TypeControlNewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # create type control
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can create type control")
    db_type_control = TypeControl(
        type_name=model.type_name,
        description=model.description,
        preview_url=model.preview_image  # Assuming the model uses "preview_image"
    )
    db.add(db_type_control)
    await db.commit()
    await db.refresh(db_type_control)
    for version_id in model.associated_versions:
        # Using the association table directly
        stmt = sdmodelversion_typecontrol_association.insert().values(
            sdmodelversion_id=version_id,
            typecontrol_id=db_type_control.id
        )
        await db.execute(stmt)
    
    await db.commit()
    return {
        "type_name": db_type_control.type_name,
        "description": db_type_control.description,
        "preview_image": db_type_control.preview_url,  # Map from preview_url to preview_image
        "id": db_type_control.id
    }


@router.get("/list", response_model=List[dict])
async def get_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # get list of models
    if current_user.role != UserRole.SUPER_ADMIN and current_user.role != UserRole.ORGANIZATION and current_user.role != UserRole.MEMBER :
        raise HTTPException(status_code=403, detail="Only super admin and admin can get list and member can get list")
    
    # Fetch data from the database
    result = await db.execute(select(Model).options(joinedload(Model.category)))
    items = result.scalars().all()

    # Construct response data with only non-None values
    response_data = [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "category": item.category.name if item.category else None,
            "preview_url": (
                item.preview_url
                if item.preview_url.startswith("data:image") or item.preview_url.startswith("http")
                else "data:image/png;base64," + item.preview_url
            ),
        }
        for item in items
    ]

    
    return response_data



# Tags endpoints


@router.get("/type-controls/tags", response_model=List[SdModelVersionResponse])
async def get_tags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # get list of tags
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get tags")
    
    result = await db.execute(select(SdModelVersion))
    tags = result.scalars().all()
    return tags



# Category endpoints


@router.get("/category", response_model=List[ModelCategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # get list of categories
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get categories")
    
    result = await db.execute(select(ModelCategoryTable))
    categories = result.scalars().all()
    return categories

@router.post("/category", response_model=ModelCategoryResponse)
async def create_category(
    model: ModelCategoryBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # create category
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can create category")
    
    db_category = ModelCategoryTable(
        name=model.name
    )
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.put("/category/{category_id}", response_model=ModelCategoryResponse)
async def update_category(
    category_id: int,
    model: ModelCategoryBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # update category
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can update category")
    
    result = await db.execute(select(ModelCategoryTable).where(ModelCategoryTable.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    category.name = model.name
    await db.commit()
    await db.refresh(category)
    return category

# SD Model Version endpoints
@router.post("/sd/versions", response_model=SdModelVersionResponse)
async def create_sd_model_version(
    model: SdModelVersionBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # create sd model version
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can create sd model version")
    
    db_version = SdModelVersion(
        version_name=model.version_name
    )
    db.add(db_version)
    await db.commit()
    await db.refresh(db_version)
    
    # Explicitly load relationships
    return db_version



    



@router.get("/sd/versions", response_model=List[SdModelVersionResponse])
async def list_sd_model_versions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # list sd model versions
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can list sd model versions")
    
    result = await db.execute(
        select(SdModelVersion)
        .options(
            selectinload(SdModelVersion.sdmodels),
            selectinload(SdModelVersion.type_controls)
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/sd/versions/{version_id}", response_model=SdModelVersionResponse)
async def get_sd_model_version(
    version_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # get sd model version
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get sd model version")
    
    result = await db.execute(
        select(SdModelVersion)
        .options(
            selectinload(SdModelVersion.sdmodels),
            selectinload(SdModelVersion.type_controls)
        )
        .where(SdModelVersion.id == version_id)
    )
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="SD Model Version not found")
    return version

@router.put("/sd/versions/{version_id}", response_model=SdModelVersionResponse)
async def update_sd_model_version(
    version_id: int,
    model: SdModelVersionBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)

):
    # update sd model version
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can update sd model version")
    
    result = await db.execute(select(SdModelVersion).where(SdModelVersion.id == version_id))
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="SD Model Version not found")

    version.version_name = model.version_name
    await db.commit()
    await db.refresh(version)
    
    # Explicitly load relationships
    await db.refresh(version, attribute_names=['sdmodels', 'type_controls'])
    return version



# SD Model endpoints

@router.get("/sd", response_model=List[SdModelResponse])
async def list_sd_models(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # list sd models
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can list sd models")
    
    result = await db.execute(select(SdModel).options(joinedload(SdModel.sdmodel_version)).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/sd/{model_id}", response_model=SdModelResponse)
async def get_sd_model(model_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # get sd model
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get sd model")
    
    result = await db.execute(select(SdModel).options(joinedload(SdModel.sdmodel_version)).filter(SdModel.id == model_id))
    db_model = result.scalar_one_or_none()
    if not db_model:
        raise HTTPException(status_code=404, detail="SD Model not found")
    return db_model


@router.post("/sd", response_model=SdModelResponse)
async def create_sd_model(model: SdModelCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # create sd model
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can create sd model")
    
    db_model = SdModel(
        name=model.name,
        description=model.description,
        sdmodel_version_id=model.sdmodel_version_id 
    )
    
    db.add(db_model)
    await db.commit()
    await db.refresh(db_model)
    # Load the sdmodel_version relationship
    result = await db.execute(
        select(SdModel)
        .options(selectinload(SdModel.sdmodel_version))
        .where(SdModel.id == db_model.id)
    )
    db_model = result.scalar_one()
    return db_model
    


# Control Model endpoints


@router.get("/filteredControlnet/{sdmodel_id}", response_model=List[ControlNetResponseFiltered])
async def get_compatible_controlnets(sdmodel_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # get compatible controlnets
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get compatible controlnets")
    
    """
    Given an sdmodel_id, returns all ControlNet objects that are compatible with the SdModel.
    Compatibility is determined by whether the SdModel's version is included in the compatible
    versions (i.e., SdModelVersions) associated with the ControlNet's TypeControl.
    """
    # 1. Retrieve the SdModel with its version eagerly loaded.
    sdmodel_stmt = select(SdModel).where(SdModel.id == sdmodel_id).options(
        selectinload(SdModel.sdmodel_version)
    )
    result = await db.execute(sdmodel_stmt)
    sdmodel = result.scalar_one_or_none()
    if not sdmodel:
        raise HTTPException(status_code=404, detail="SdModel not found.")
    if not sdmodel.sdmodel_version:
        raise HTTPException(status_code=400, detail="SdModel has no assigned version.")
    
    model_version = sdmodel.sdmodel_version

    # 2. Load all ControlNet entries, eagerly loading relationships needed to check compatibility.
    # We need to load ControlModel.type_control and its associated sdmodel_versions.
    controlnet_stmt = select(ControlNet).options(
        selectinload(ControlNet.control_model)
            .selectinload(ControlModel.type_control)
            .selectinload(TypeControl.sdmodel_versions),
        selectinload(ControlNet.control_module)
            .selectinload(ControlModule.type_control)
            .selectinload(TypeControl.sdmodel_versions)
    )
    result = await db.execute(controlnet_stmt)
    controlnets = result.scalars().all()

    # 3. Filter controlnets by checking if our sdmodel's version is in the controlnet's TypeControl's sdmodel_versions.
    compatible_controlnets = []
    for cn in controlnets:
        try:
            # The "type_control" property checks that both control_model and control_module share the same one.
            type_control = cn.type_control
        except Exception:
            # Skip controlnets with inconsistent type_control.
            continue

        # Check if the version of our SdModel is among the compatible versions of this controlnet.
        if any(ver.id == model_version.id for ver in type_control.sdmodel_versions):
            compatible_controlnets.append(cn)

    # 4. Prepare a JSON-ready response. Adjust included fields as desired.
    response = [
        {
            "id": cn.id,
            "name": cn.name,
            
        }
        for cn in compatible_controlnets
    ]
    return response


@router.get("/control-models/typecontrol/{typecontrol_id}", response_model=List[ControlModelResponse])
async def get_control_models_by_typecontrol(typecontrol_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # get control models by typecontrol
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get control models by typecontrol")
    
    result = await db.execute(select(ControlModel).options(joinedload(ControlModel.type_control)).filter(ControlModel.typecontrol_id == typecontrol_id))
    return result.scalars().all()



@router.post("/control-models", response_model=ControlModelResponse)
async def create_control_model(model: ControlModelCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # create control model
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can create control model")
    
    db_model = ControlModel(
        name=model.name,
        description=model.description,
        typecontrol_id=model.typecontrol_id
    )

    db.add(db_model)
    await db.commit()
    await db.refresh(db_model)
    
    # Load the type_control relationship
    result = await db.execute(
        select(ControlModel)
        .options(selectinload(ControlModel.type_control))
        .where(ControlModel.id == db_model.id)
    )
    db_model = result.scalar_one()
    return db_model


@router.get("/control-models", response_model=List[ControlModelResponse])
async def list_control_models(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # list control models
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can list control models")
    
    # result = await db.execute(select(ControlModel).offset(skip).limit(limit))
    result = await db.execute(
        select(ControlModel)
        .options(
            selectinload(ControlModel.type_control)
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/control-models/{model_id}", response_model=ControlModelResponse)
async def get_control_model(model_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # get control model
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get control model")
    
    result = await db.execute(select(ControlModel).filter(ControlModel.id == model_id))
    db_model = result.scalar_one_or_none()
    if not db_model:
        raise HTTPException(status_code=404, detail="Control Model not found")
    return db_model


@router.put("/control-models/{model_id}", response_model=ControlModelResponse)
async def update_control_model(model_id: int, model: ControlModelCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # update control model
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can update control model")
    
    result = await db.execute(select(ControlModel).filter(ControlModel.id == model_id))
    db_model = result.scalar_one_or_none()
    if not db_model:
        raise HTTPException(status_code=404, detail="Control Model not found")

    for key, value in model.model_dump().items():
        setattr(db_model, key, value)

    await db.commit()
    await db.refresh(db_model)
    return db_model


@router.delete("/control-models/{model_id}")
async def delete_control_model(model_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # delete control model
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can delete control model")
    
    result = await db.execute(select(ControlModel).filter(ControlModel.id == model_id))
    db_model = result.scalar_one_or_none()
    if not db_model:
        raise HTTPException(status_code=404, detail="Control Model not found")

    await db.delete(db_model)
    await db.commit()
    return {"message": "Control Model deleted successfully"}

# Control Module endpoints


@router.get("/control-modules/typecontrol/{typecontrol_id}", response_model=List[ControlModuleResponse])
async def get_control_modules_by_typecontrol(typecontrol_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # get control modules by typecontrol
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get control modules by typecontrol")
    
    result = await db.execute(select(ControlModule).options(joinedload(ControlModule.type_control)).filter(ControlModule.typecontrol_id == typecontrol_id))
    return result.scalars().all()


@router.post("/control-modules", response_model=ControlModuleResponse)
async def create_control_module(module: ControlModuleCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # create control module
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can create control module")
    
    db_module = ControlModule(
        name=module.name,
        description=module.description,
        typecontrol_id=module.typecontrol_id
    )

    db.add(db_module)
    await db.commit()
    await db.refresh(db_module)
    
    # Load the type_control relationship
    result = await db.execute(
        select(ControlModule)
        .options(selectinload(ControlModule.type_control))
        .where(ControlModule.id == db_module.id)
    )
    db_module = result.scalar_one()
    return db_module


@router.get("/control-modules", response_model=List[ControlModuleResponse])
async def list_control_modules(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # list control modules
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can list control modules")
    
    # result = await db.execute(select(ControlModule).offset(skip).limit(limit))
    result = await db.execute(
        select(ControlModule)
        .options(
            selectinload(ControlModule.type_control)
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/control-modules/{module_id}", response_model=ControlModuleResponse)
async def get_control_module(module_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # get control module
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get control module")
    
    result = await db.execute(select(ControlModule).filter(ControlModule.id == module_id))
    db_module = result.scalar_one_or_none()
    if not db_module:
        raise HTTPException(status_code=404, detail="Control Module not found")
    return db_module


@router.put("/control-modules/{module_id}", response_model=ControlModuleResponse)
async def update_control_module(module_id: int, module: ControlModuleCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # update control module
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can update control module")
    
    result = await db.execute(select(ControlModule).filter(ControlModule.id == module_id))
    db_module = result.scalar_one_or_none()
    if not db_module:
        raise HTTPException(status_code=404, detail="Control Module not found")

    for key, value in module.model_dump().items():
        setattr(db_module, key, value)

    await db.commit()
    await db.refresh(db_module)
    return db_module


@router.delete("/control-modules/{module_id}")
async def delete_control_module(module_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # delete control module
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can delete control module")
    
    result = await db.execute(select(ControlModule).filter(ControlModule.id == module_id))
    db_module = result.scalar_one_or_none()
    if not db_module:
        raise HTTPException(status_code=404, detail="Control Module not found")

    await db.delete(db_module)
    await db.commit()
    return {"message": "Control Module deleted successfully"}

# Sampler Mode endpoints


@router.post("/sampler-modes", response_model=SamplerModeResponse)
async def create_sampler_mode(sampler: SamplerModeCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # create sampler mode
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can create sampler mode")
    
    db_sampler = SamplerModeTable(**sampler.model_dump())
    db.add(db_sampler)
    await db.commit()
    await db.refresh(db_sampler)
    return db_sampler


@router.get("/sampler-modes", response_model=List[SamplerModeResponse])
async def list_sampler_modes(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # list sampler modes
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can list sampler modes")
    
    result = await db.execute(select(SamplerModeTable).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/sampler-modes/{sampler_id}", response_model=SamplerModeResponse)
async def get_sampler_mode(sampler_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # get sampler mode
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get sampler mode")
    
    result = await db.execute(select(SamplerModeTable).filter(SamplerModeTable.id == sampler_id))
    db_sampler = result.scalar_one_or_none()
    if not db_sampler:
        raise HTTPException(status_code=404, detail="Sampler Mode not found")
    return db_sampler


@router.put("/sampler-modes/{sampler_id}", response_model=SamplerModeResponse)
async def update_sampler_mode(sampler_id: int, sampler: SamplerModeCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # update sampler mode
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can update sampler mode")
    
    result = await db.execute(select(SamplerModeTable).filter(SamplerModeTable.id == sampler_id))
    db_sampler = result.scalar_one_or_none()
    if not db_sampler:
        raise HTTPException(status_code=404, detail="Sampler Mode not found")

    for key, value in sampler.model_dump().items():
        setattr(db_sampler, key, value)

    await db.commit()
    await db.refresh(db_sampler)
    return db_sampler


@router.delete("/sampler-modes/{sampler_id}")
async def delete_sampler_mode(sampler_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # delete sampler mode
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can delete sampler mode")
    
    result = await db.execute(select(SamplerModeTable).filter(SamplerModeTable.id == sampler_id))
    db_sampler = result.scalar_one_or_none()
    if not db_sampler:
        raise HTTPException(status_code=404, detail="Sampler Mode not found")

    await db.delete(db_sampler)
    await db.commit()
    return {"message": "Sampler Mode deleted successfully"}

# ControlNet endpoints
@router.get("/controlnets/compatible/{sdmodel_id}", response_model=List[ControlNetResponse])
async def get_compatible_controlnets(sdmodel_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # get compatible controlnets
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get compatible controlnets")
    
    """
    Given an SdModel id, this endpoint does the following:
      1. Loads the full SdModel (including its SdModelVersion) to extract the version_name.
      2. Loads all ControlNets with the necessary relationships:
         - ControlModel -> TypeControl (which contains the associated SD model versions)
         - ControlModule -> TypeControl.
      3. For each ControlNet, it uses the property 'type_control' (which verifies the consistency of the ControlModel
         and ControlModule associations) to retrieve the TypeControl.
      4. It then checks whether the given SdModel's version_name is present in the list of version_names associated with that TypeControl.
      5. Only the ControlNets that pass this compatibility check are returned.
    """
    # 1. Get the SD model with its associated version
    result = await db.execute(
        select(SdModel)
        .options(joinedload(SdModel.sdmodel_version))
        .where(SdModel.id == sdmodel_id)
    )
    sd_model = result.scalar_one_or_none()
    if not sd_model:
        raise HTTPException(status_code=404, detail="SD Model not found")
    if not sd_model.sdmodel_version:
        raise HTTPException(status_code=400, detail="SD Model has no associated version")
    
    # Extract the version name for compatibility check.
    version_name = sd_model.sdmodel_version.version_name

    # 2. Load all ControlNets and eagerly load the relationships required to check compatibility.
    result = await db.execute(
        select(ControlNet)
        .options(
            # For the control model: load its type control and, from that, its associated sdmodel_versions.
            selectinload(ControlNet.control_model)
                .selectinload(ControlModel.type_control)
                .selectinload(TypeControl.sdmodel_versions),
            # For the control module: load its type control.
            selectinload(ControlNet.control_module)
                .selectinload(ControlModule.type_control)
            # Optionally, you can load other relationships if required.
        )
    )
    controlnets = result.scalars().all()

    # 3. Filter each ControlNet: check if the SD model's version_name is among the associated version names of the TypeControl.
    compatible_controlnets = []
    for cn in controlnets:
        try:
            # The property "type_control" will raise an exception if the control_model and control_module are not consistent.
            tc = cn.type_control
        except Exception:
            # Skip controlnets with inconsistent type control definitions.
            continue

        # Build a list of the associated version names from the TypeControl.
        associated_versions = [v.version_name for v in tc.sdmodel_versions]
        if version_name in associated_versions:
            compatible_controlnets.append(cn)

    return compatible_controlnets

@router.post("/controlnet", response_model=ControlNetResponse)
async def create_controlnet(controlnet: ControlNetCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # create controlnet
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can create controlnet")
    
    db_controlnet = ControlNet(
        name=controlnet.name,
        description=controlnet.description,
        enabled=controlnet.enabled,
        control_mode=controlnet.control_mode,
        resize_mode=controlnet.resize_mode,
        guidance_start=controlnet.guidance_start,
        guidance_end=controlnet.guidance_end,
        weight=controlnet.weight,
        control_model_id=controlnet.control_model_id,
        control_module_id=controlnet.control_module_id
    )
    db.add(db_controlnet)
    await db.commit()
    await db.refresh(db_controlnet)
    
    # Eagerly load relationships
    result = await db.execute(
        select(ControlNet)
        .options(
            selectinload(ControlNet.control_model).selectinload(ControlModel.type_control),
            selectinload(ControlNet.control_module).selectinload(ControlModule.type_control)
        )
        .where(ControlNet.id == db_controlnet.id)
    )
    db_controlnet = result.scalar_one()
    return db_controlnet

@router.get("/controlnet", response_model=List[ControlNetResponse])
async def list_controlnets(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # list controlnets
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can list controlnets")
    
    # result = await db.execute(select(ControlNet).offset(skip).limit(limit))
    result = await db.execute(
        select(ControlNet)
        .options(
            selectinload(ControlNet.control_model).selectinload(
                ControlModel.type_control),
            selectinload(ControlNet.control_module).selectinload(
                ControlModule.type_control),
            selectinload(ControlNet.models)
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/controlnet/{controlnet_id}", response_model=ControlNetResponse)
async def get_controlnet(controlnet_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # get controlnet
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get controlnet")
    
    result = await db.execute(select(ControlNet).filter(ControlNet.id == controlnet_id))
    db_controlnet = result.scalar_one_or_none()
    if not db_controlnet:
        raise HTTPException(status_code=404, detail="ControlNet not found")
    return db_controlnet


@router.put("/controlnet/{controlnet_id}", response_model=ControlNetResponse)
async def update_controlnet(controlnet_id: int, controlnet: ControlNetCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # update controlnet
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can update controlnet")
    
    result = await db.execute(select(ControlNet).filter(ControlNet.id == controlnet_id))
    db_controlnet = result.scalar_one_or_none()
    if not db_controlnet:
        raise HTTPException(status_code=404, detail="ControlNet not found")

    for key, value in controlnet.model_dump().items():
        setattr(db_controlnet, key, value)

    await db.commit()
    await db.refresh(db_controlnet)
    return db_controlnet


@router.delete("/controlnet/{controlnet_id}")
async def delete_controlnet(controlnet_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # delete controlnet
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can delete controlnet")
    
    result = await db.execute(select(ControlNet).filter(ControlNet.id == controlnet_id))
    db_controlnet = result.scalar_one_or_none()
    if not db_controlnet:
        raise HTTPException(status_code=404, detail="ControlNet not found")

    await db.delete(db_controlnet)
    await db.commit()
    return {"message": "ControlNet deleted successfully"}

# Type Controls endpoints
# Pydantic models remain the same as defined

@router.get("/type-controls", response_model=List[TypeControlResponse])
async def list_type_controls(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # list type controls
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can list type controls")
    
    # Query the database and pre-load relationships
    result = await db.execute(
        select(TypeControl)
        .options(joinedload(TypeControl.sdmodel_versions))  # Pre-load sdmodel_versions
        .offset(skip)
        .limit(limit)
    )
    type_controls = result.scalars().unique().all()  # Ensure unique results

    # Populate associated_versions explicitly
    response = [
        TypeControlResponse(
            id=tc.id,
            type_name=tc.type_name,
            description=tc.description,
            preview_url=tc.preview_url,
            associated_versions=[
                SdModelVersionResponse(
                    id=version.id,
                    version_name=version.version_name,
                    created_at=version.created_at
                )
                for version in tc.sdmodel_versions  # Map to Pydantic model
            ]
        )
        for tc in type_controls
    ]
    return response  # Return the properly constructed response




@router.get("/type-controls/{type_id}", response_model=TypeControlResponse)
async def get_type_control(type_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # get type control
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get type control")
    
    # Query the database and pre-load relationships
    result = await db.execute(
        select(TypeControl)
        .options(joinedload(TypeControl.sdmodel_versions))  # Pre-load sdmodel_versions
        .filter(TypeControl.id == type_id)
    )
    db_type = result.scalars().unique().one_or_none()  # Ensure single result and handle duplicates

    if not db_type:
        raise HTTPException(status_code=404, detail="Type Control not found")

    # Construct the response model explicitly
    response = TypeControlResponse(
        id=db_type.id,
        type_name=db_type.type_name,
        description=db_type.description,
        preview_url=db_type.preview_url,
        associated_versions=[
            SdModelVersionResponse(
                id=version.id,
                version_name=version.version_name,
                created_at=version.created_at
            )
            for version in db_type.sdmodel_versions  # Map each associated version
        ]
    )
    return response









# Sampler Types endpoints


@router.get("/sampler-types", response_model=List[SamplerTypeResponse])
async def list_sampler_types(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # list sampler types
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can list sampler types")
    
    result = await db.execute(select(SamplerTypeTable).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/sampler-types", response_model=SamplerTypeResponse)
async def create_sampler_type(sampler_type: SamplerTypeBase, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # create sampler type
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can create sampler type")
    
    db_type = SamplerTypeTable(
        name=sampler_type.name
    )
    db.add(db_type)
    await db.commit()
    await db.refresh(db_type)
    return db_type

@router.get("/sampler-types/{type_id}", response_model=SamplerTypeResponse)
async def get_sampler_type(type_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # get sampler type
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can get sampler type")
    
    result = await db.execute(select(SamplerTypeTable).filter(SamplerTypeTable.id == type_id))
    db_type = result.scalar_one_or_none()
    if not db_type:
        raise HTTPException(status_code=404, detail="Sampler Type not found")
    return db_type

# Base Model endpoints


@router.post("/")
async def create_controlnet(model: ModelCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # create model
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can create model")
    
    db_model = Model(
        name=model.name,
        description=model.description,
        type=model.type,
        sdmodel_id=model.sdmodel_id,
        active=model.active,
        width=model.width,
        height=model.height,
        steps=model.steps,
        cfg_scale=model.cfg_scale,
        seed=model.seed,
        save_images=model.save_images,
        resize_mode=model.resize_mode,
        gendre=model.gendre,
        sampler_mode_id=model.sampler_mode_id,
        sampler_type_id=model.sampler_type_id,
        prompt=model.prompt,
        negative_prompt=model.negative_prompt,
        preview_url=model.preview_image,
        category_id=model.categorie_id
    )
    db.add(db_model)
    await db.commit()
    await db.refresh(db_model)
    for version_id in model.listcontrolnets:
        # Using the association table directly
        stmt = model_controlnet_association.insert().values(
            controlnet_id=version_id,
            model_id=db_model.id
        )
        await db.execute(stmt)
    
    await db.commit()
    




@router.get("/", response_model=List[ModelResponse])
async def list_models(current_user: User = Depends(get_current_user),skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    # list models
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can list models")
    result = await db.execute(
        select(Model)
        .options(
            selectinload(Model.sdmodel).selectinload(SdModel.sdmodel_version),
            selectinload(Model.sampler_mode),
            selectinload(Model.sampler_type),
            selectinload(Model.category),
            selectinload(Model.controlnets).selectinload(
                ControlNet.control_model).selectinload(ControlModel.type_control),
            selectinload(Model.controlnets).selectinload(
                ControlNet.control_module).selectinload(ControlModule.type_control),
            selectinload(Model.controlnets).selectinload(ControlNet.models)
        )
        .offset(skip)
        .limit(limit)
    )
    models = result.scalars().all()
    
    for m in models:
        m.resize_mode_name = m.resize_mode.name
        if not m.preview_url.startswith("data:image") and not m.preview_url.startswith("http"):
            m.preview_url = "data:image/png;base64," + m.preview_url

    return models

@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(model_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # get model
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can get model")
    
    result = await db.execute(
        select(Model)
        .options(
            selectinload(Model.sdmodel),
            selectinload(Model.sampler_mode),
            selectinload(Model.sampler_type),
            selectinload(Model.category),
            selectinload(Model.controlnets).selectinload(
                ControlNet.control_model).selectinload(ControlModel.type_control),
            selectinload(Model.controlnets).selectinload(
                ControlNet.control_module).selectinload(ControlModule.type_control),
            selectinload(Model.controlnets).selectinload(ControlNet.models)
        )
        .filter(Model.id == model_id)
    )
    db_model = result.scalar_one_or_none()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    return db_model

from pathlib import Path
from typing import List, Dict, Set
from urllib.parse import urlparse
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from PIL import Image, ImageChops
import io
import base64
import numpy as np

def load_image_from_png(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")

def load_image_from_base64(b64_string: str) -> Image.Image:
    image_data = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_data)).convert("RGB")

def compare_images(img1: Image.Image, img2: Image.Image) -> int:
    """Compare two images and return the total difference in pixel values."""
    # Resize images to the smallest size among both to avoid dimension mismatch
    min_width = min(img1.width, img2.width)
    min_height = min(img1.height, img2.height)
    img1_resized = img1.resize((min_width, min_height))
    img2_resized = img2.resize((min_width, min_height))

    # Convert to numpy arrays
    arr1 = np.array(img1_resized)
    arr2 = np.array(img2_resized)

    # Compute difference
    diff = np.abs(arr1.astype(int) - arr2.astype(int))
    total_diff = np.sum(diff)

    return int(total_diff)


@router.get("/miss/base-models")
async def get_missing_base_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this endpoint"
        )
    l = []
    params_dir = Path("database/data/params")
    if not params_dir.exists():
        return {"missing_images": [], "comparisons": []}

    image_files = [f for f in params_dir.iterdir() if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
    list_png_path = [params_dir / Path(png_path).name for png_path in image_files]
    result = await db.execute(select(Model.preview_url))
    db_images = result.scalars().all()  # list of all matching preview_url strings
    for i in db_images:
        for j in list_png_path:
            try:
                img1 = load_image_from_png(j)
                img2 = load_image_from_base64(i)
            except Exception as e:
                print(f"Error loading images: {str(e)}")
                import traceback
                traceback.print_exc()
            difference = compare_images(img1, img2)
            if difference == 0:
                l.append(j)
            print(f"Comparison result: {difference}")
            break  # Exit the async for loop after successful execution
    
    k = list(set(list_png_path) - set(l))
    result = []
    for path_str in k:
        path = Path(path_str)
        if path.exists() and path.is_file():
            with open(path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
            result.append({
                "name": path.name,
                "image": img_b64
            })
    return result


@router.get("/miss/base-models/paginated")
async def get_missing_base_models(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this endpoint"
        )
    l = []
    params_dir = Path("database/data/params")
    if not params_dir.exists():
        return {"missing_images": [], "total": 0, "page": page, "page_size": page_size}

    image_files = [f for f in params_dir.iterdir() if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
    list_png_path = [params_dir / Path(png_path).name for png_path in image_files]
    result = await db.execute(select(Model.preview_url))
    db_images = result.scalars().all()

    for i in db_images:
        for j in list_png_path:
            try:
                img1 = load_image_from_png(j)
                img2 = load_image_from_base64(i)
            except Exception as e:
                print(f"Error loading images: {str(e)}")
                import traceback
                traceback.print_exc()
            difference = compare_images(img1, img2)
            if difference == 0:
                l.append(j)
            print(f"Comparison result: {difference}")
            break

    missing_paths = list(set(list_png_path) - set(l))
    
    # Pagination slice calculation
    start = (page - 1) * page_size
    end = start + page_size
    paginated_paths = missing_paths[start:end]

    result = []
    for path in paginated_paths:
        if path.exists() and path.is_file():
            with open(path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
            result.append({
                "name": path.name,
                "image": img_b64
            })

    return {
        "missing_images": result,
        "total": len(missing_paths),
        "page": page,
        "page_size": page_size,
    }


def parse_txt_to_model(text: str) -> ModelBase:
    # Extract prompt (everything before "Negative prompt:")
    prompt_match = re.search(r"^(.*?)Negative prompt:", text, re.DOTALL | re.IGNORECASE)
    prompt = prompt_match.group(1).strip() if prompt_match else None

    # Extract negative prompt (between "Negative prompt:" and first parameter line)
    neg_prompt_match = re.search(r"Negative prompt:(.*?)(Steps:|Sampler:|CFG scale:|Seed:|Size:|Model hash:|Model:|Version:)", text, re.DOTALL | re.IGNORECASE)
    negative_prompt = neg_prompt_match.group(1).strip() if neg_prompt_match else None

    # Extract Steps
    steps_match = re.search(r"Steps:\s*(\d+)", text)
    steps = int(steps_match.group(1)) if steps_match else None

    # Extract Sampler (for sampler_type_id, map string to id as you wish)
    sampler_match = re.search(r"Sampler:\s*([A-Za-z0-9_]+)", text)
    sampler_type = sampler_match.group(1) if sampler_match else None

    # Extract CFG scale
    cfg_match = re.search(r"CFG scale:\s*([\d\.]+)", text)
    cfg_scale = float(cfg_match.group(1)) if cfg_match else 7.0

    # Extract Seed
    seed_match = re.search(r"Seed:\s*(\d+)", text)
    seed = int(seed_match.group(1)) if seed_match else None

    # Extract Size
    size_match = re.search(r"Size:\s*(\d+)x(\d+)", text)
    width = int(size_match.group(1)) if size_match else None
    height = int(size_match.group(2)) if size_match else None

    # Extract Model name
    model_match = re.search(r"Model:\s*([\w_\-]+)", text)
    model_name = model_match.group(1) if model_match else None

    # Map sampler_type to sampler_type_id (example static mapping)
    sampler_type_id_map = {"Euler": 1, "LMS": 2, "DDIM": 3}
    sampler_type_id = sampler_type_id_map.get(sampler_type, 0)

    # Example fixed sampler_mode_id (could parse or adjust)
    sampler_mode_id = 1

    # Compose the Pydantic model instance
    model = ModelBase(
        name=model_name or "Unnamed Model",
        prompt=prompt,
        negative_prompt=negative_prompt,
        steps=steps,
        cfg_scale=cfg_scale,
        seed=seed,
        width=width,
        height=height,
        sampler_mode_id=sampler_mode_id,
        sampler_type_id=sampler_type_id,
        active=True,
    )

    return model

import aiofiles
import re

class ModelsIdRequest(BaseModel):
    models_id: List[str]
def safe_extract(content: str, key: str) -> str | None:
    parts = content.split(key)
    if len(parts) > 1:
        # Sometimes keys might be followed by other keys on the same line,
        # so we split by newline to get just the value for this key.
        value = parts[1].split('\n')[0].strip()
        return value
    return None

@router.post("/add_models")
async def add_models(
    request: ModelsIdRequest, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can add models")

    params_dir = Path("database/data/params")
    result = []

    for model_id in request.models_id:
        if not model_id.replace(".", "").isalnum():
            continue

        model_name = model_id.split(".")[0]
        file_path = params_dir / f"{model_name}.txt"

        if not file_path.exists() or not file_path.is_file():
            continue

        async with aiofiles.open(file_path, mode="r") as f:
            content = await f.read()

        # Extract the prompt (everything before "Negative prompt:")
        prompt = content.split("Negative prompt:")[0].strip()

        # Extract the negative prompt (everything after "Negative prompt:" and before "Steps:")
        negative_prompt = content.split("Negative prompt:")[1].split("Steps:")[0].strip()

        # Extract the Steps line (everything after "Steps:")
        steps_line = content.split("Steps:")[1].strip()

        # Use regex to parse fields inside the steps line
        def extract_value(pattern, text):
            match = re.search(pattern, text)
            return match.group(1).strip() if match else None

        steps = extract_value(r"^(\d+)", steps_line)  # The number right after "Steps:"
        sampler_type = extract_value(r"Sampler:\s*([^,]+)", steps_line)
        cfg_scale = extract_value(r"CFG scale:\s*([^,]+)", steps_line)
        seed = extract_value(r"Seed:\s*([^,]+)", steps_line)
        size = extract_value(r"Size:\s*([^,]+)", steps_line)

        width = None
        height = None
        if size:
            size_match = re.match(r"(\d+)x(\d+)", size)
            if size_match:
                width = size_match.group(1)
                height = size_match.group(2)

        result.append({
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": -1,
            "width": width,
            "height": height,
            "sampler_type": sampler_type
        })

    return result


ModelResponse.model_rebuild()
ControlNetResponse.model_rebuild()


