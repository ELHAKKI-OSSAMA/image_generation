from sqlalchemy.orm import Session
from database.models import Model, ControlNet  # Replace with your actual models
from database.schemas.sd_models_schema import  ControlNetArgPayload, AlwaysOnScriptsPayload, ControlNetScriptPayload
from fastapi import HTTPException

def get_model_payload_by_id(model_id: int, session: Session,image_input: str):
    # Fetch the SdModel record and its related data
    model_record = session.query(Model).filter(Model.id == model_id).first()

    if not model_record:
        raise HTTPException(status_code=404, detail=f"Model with ID {model_id} not found")

    # Fetch associated ControlNet data
    # Fetch associated ControlNet records using the many-to-many relationship
    controlnets_records = (
        session.query(ControlNet)
        .join(ControlNet.models)  # Join the many-to-many association
        .filter(Model.id == model_id)  # Filter by model_id
        .all()
    )   
    # Create `ControlNetArgPayload` instances dynamically
    controlnet_args = []
    for controlnet in controlnets_records:
        controlnet_args.append(ControlNetArgPayload(
            enabled=controlnet.enabled,
            model=controlnet.control_model.name,
            module=controlnet.control_module.name,
            image={
                "image": image_input,
            },
            guidance_start=controlnet.guidance_start,
            guidance_end=controlnet.guidance_end,
            weight=controlnet.weight,
            control_mode=controlnet.control_mode,
            resize_mode=controlnet.resize_mode
        ))

    # Create `ControlNetScriptPayload`
    controlnet_script_payload = ControlNetScriptPayload(
        args=controlnet_args
    )

    # Create the nested payloads
    alwayson_scripts_payload = None
    if controlnet_args:
        controlnet_script_payload = ControlNetScriptPayload(args=controlnet_args)
        alwayson_scripts_payload = AlwaysOnScriptsPayload(ControlNet=controlnet_script_payload)

    # Create the final payload using the CreateModelPayload schema
    payload_data = {
        "model": model_record.name,
        "prompt": model_record.prompt,
        "negative_prompt": model_record.negative_prompt,
        "resize_mode": model_record.resize_mode,
        "steps": model_record.steps,
        "save_images": model_record.save_images,
        "seed": model_record.seed,
        "width": model_record.width,
        "height": model_record.height,
        "cfg_scale": model_record.cfg_scale,
        "sampler": "euler a",  # Adjust or fetch this value as needed
    }

    # Add `alwayson_scripts` only if it exists
    if alwayson_scripts_payload:
        payload_data["alwayson_scripts"] = alwayson_scripts_payload

    return payload_data