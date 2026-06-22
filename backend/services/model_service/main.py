# model_service.py

from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional

from core.database import async_session, engine, Base,get_db  # assumes these are defined in your connection file
from sqlalchemy.orm import Session
from database.models import Model  # your SQLAlchemy model for 'Model'
from database.schemas.sd_models_schema import ModelSchema  # Pydantic schema for the Model
from services.model_service.payload import get_model_payload_by_id
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Model Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "model_service"}

@app.get("/api/models", response_model=List[ModelSchema])
def get_models(db: Session = Depends(get_db)):
    models = db.query(Model).all()
    return models

@app.get("/api/models")
def get_models(db: Session = Depends(get_db)):
    models = db.query(Model).all()
    return [
        {
            "id": model.id,
            "name": model.name,
            "category": model.category,
            "description": model.description,
            "preview": "data:image/png;base64,"+model.preview_url
        }
        for model in models
    ]

@app.get("/models/{model_id}", response_model=ModelSchema)
def get_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(Model).filter(Model.id == model_id).first()
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@app.get("/api/models/payload/{model_id}", response_model=dict)
async def get_model_payload(
    model_id: int,
    imagebase64: str = Query("default_base64_value"),
    db: Session = Depends(get_db),
):
    try:
        payload = get_model_payload_by_id(model_id, db, imagebase64)
        return payload
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
