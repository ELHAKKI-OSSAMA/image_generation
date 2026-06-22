from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from .config import settings

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = None):
    if not credentials:
        raise HTTPException(status_code=403, detail="Invalid authorization code.")
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

class ServiceAuthMiddleware:
    async def __call__(self, request: Request, call_next):
        if request.url.path.startswith("/api"):
            credentials = await security(request)
            await verify_token(credentials)
        
        response = await call_next(request)
        return response
