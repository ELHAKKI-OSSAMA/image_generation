"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from shared.config import settings

app = FastAPI(title="API Gateway")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def proxy_request(request: Request, service_url: str) -> dict:

    client = httpx.AsyncClient(base_url=service_url)
    
    # Get request body if present
    body = await request.body()
    
    try:
        response = await client.request(
            method=request.method,
            url=str(request.url.path),
            content=body,
            headers=dict(request.headers),
            params=dict(request.query_params),
        )
        return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")
    finally:
        await client.aclose()

# Model Service Routes
@app.api_route("/api/models/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def model_routes(request: Request, path: str):
    return await proxy_request(request, settings.MODEL_SERVICE_URL)

# Image Service Routes
@app.api_route("/api/images/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def image_routes(request: Request, path: str):
    return await proxy_request(request, settings.IMAGE_SERVICE_URL)

# User Service Routes
@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def user_routes(request: Request, path: str):
    return await proxy_request(request, settings.USER_SERVICE_URL)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


"""


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from fastapi.responses import JSONResponse

app = FastAPI(title="API Gateway")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Microservices URLs
MODEL_SERVICE_URL = "http://localhost:8001"
EVENT_SERVICE_URL = "http://localhost:8002"
IMAGE_SERVICE_URL = "http://localhost:8003"

import httpx
from fastapi import HTTPException
from fastapi.responses import JSONResponse

async def forward_request(url: str, method="GET", data=None):
    async with httpx.AsyncClient() as client:
        if method.upper() == "GET":
            response = await client.request(method, url, params=data)
        else:
            response = await client.request(method, url, json=data)
        
        if response.status_code != 200:
            # For debugging, log the complete response text
            error_text = response.text
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error forwarding request: {error_text}"
            )
        
        try:
            json_content = response.json()
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Error parsing JSON from upstream service: {e}"
            )
        
        return JSONResponse(
            content=json_content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )


@app.get("/a")
async def root():
    return {"message": "API Gateway Running"}

@app.get("/api/model/health")
async def model_health():
    return await forward_request(f"{MODEL_SERVICE_URL}/api/health")

@app.get("/api/events")
async def get_events():
    return await forward_request(f"{EVENT_SERVICE_URL}/api/events")

@app.get("/api/models")
async def get_models():
    return await forward_request(f"{MODEL_SERVICE_URL}/api/models", method="GET")

@app.post("/api/images/generate")
async def generate_image(data: dict):
    return await forward_request(f"{IMAGE_SERVICE_URL}/api/images/generate", "POST", data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
