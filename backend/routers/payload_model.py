from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import os
from dotenv import load_dotenv

from database.models import Model, ControlNet
from database.schemas.sd_models_schema import (
    ControlNetArgPayload,
    AlwaysOnScriptsPayload,
    ControlNetScriptPayload,
    CreateModelPayload
)
from core.database import get_db

# Load environment variables
load_dotenv()

# Get the API key from environment variables
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")
if not INTERNAL_API_KEY:
    raise ValueError("INTERNAL_API_KEY environment variable not set")

# API Key validation function
async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return True

router = APIRouter(
    prefix="/payloads",
    tags=["payloads"]
)

@router.get("/{model_id}", response_model=CreateModelPayload)
async def get_model_payload(
    model_id: int,
    image_input: str = "",
    session: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    # get model payload from database to send it to sdapi
    # Asynchronously fetch the Model record, eagerly loading the sampler_mode relationship
    result = await session.execute(
        select(Model)
        .options(selectinload(Model.sampler_mode))
        .where(Model.id == model_id)
    )
    model_record = result.scalar_one_or_none()
    
    if not model_record:
        raise HTTPException(status_code=404, detail=f"Model with ID {model_id} not found")

    result2 = await session.execute(
        select(Model)
        .options(selectinload(Model.sdmodel))
        .where(Model.id == model_id)
    )
    model_record = result2.scalar_one_or_none()
    if not model_record:
        raise HTTPException(status_code=404, detail="Model not found")

    # Asynchronously fetch ControlNet records and eagerly load ControlNet's relationships
    controlnet_result = await session.execute(
        select(ControlNet)
        .options(
            selectinload(ControlNet.control_model),
            selectinload(ControlNet.control_module)
        )
        .join(ControlNet.models)  # Adjust this if your association attribute is different
        .where(Model.id == model_id)
    )
    controlnet_records = controlnet_result.scalars().all()

    # Create ControlNetArgPayload instances dynamically for each ControlNet record
    controlnet_args = [
        ControlNetArgPayload(
            enabled=controlnet.enabled,
            model=controlnet.control_model.name if controlnet.control_model else "Default Model",
            module=controlnet.control_module.name if controlnet.control_module else "Default Module",
            image={"image": model_record.preview_url},
            guidance_start=controlnet.guidance_start,
            guidance_end=controlnet.guidance_end,
            weight=controlnet.weight,
            control_mode=controlnet.control_mode,
            resize_mode=controlnet.resize_mode,
            pixel_perfect=True


        )
        for controlnet in controlnet_records
    ]

    alwayson_scripts_payload = None
    if controlnet_args:
        alwayson_scripts_payload = AlwaysOnScriptsPayload(
            ControlNet=ControlNetScriptPayload(args=controlnet_args)
        )

    # Construct the final payload
    payload_data = {
        "model": model_record.sdmodel.name if model_record.sdmodel else "Default Model",
        "prompt": model_record.prompt,
        "negative_prompt": model_record.negative_prompt,
        "resize_mode": model_record.resize_mode,
        "steps": model_record.steps,
        "save_images": model_record.save_images,
        "seed": model_record.seed,
        "width": model_record.width,
        "height": model_record.height,
        "cfg_scale": model_record.cfg_scale,
        "sampler": model_record.sampler_mode.name if model_record.sampler_mode else "sampler mode",  # Uses the eagerly loaded sampler_mode
        "batch_size": 1,
        "denoising_strength": 0  ,
        "n_iter":1

    }

    if alwayson_scripts_payload:
        payload_data["alwayson_scripts"] = alwayson_scripts_payload

    return payload_data
