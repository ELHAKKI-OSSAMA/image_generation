from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from shared.middleware import ServiceAuthMiddleware
from shared.config import settings

app = FastAPI(title="User Service")

# Add authentication middleware for protected routes
app.middleware("http")(ServiceAuthMiddleware())

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"  # Default role is user

class User(UserBase):
    id: int
    role: str
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

# In-memory storage (replace with database in production)
users_db = [
    {
        "id": 1,
        "email": "admin@example.com",
        "full_name": "Admin User",
        "role": "admin",
        "hashed_password": pwd_context.hash("admin123"),  # Change in production
        "is_active": True
    }
]

def get_user_by_email(email: str):
    return next((user for user in users_db if user["email"] == email), None)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# Routes
@app.post("/api/auth/register", response_model=User)
async def register(user: UserCreate):
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = {
        "id": len(users_db) + 1,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "hashed_password": hashed_password,
        "is_active": True
    }
    users_db.append(new_user)
    
    return {**new_user, "password": None}

@app.post("/api/auth/login", response_model=Token)
async def login(email: EmailStr, password: str):
    user = get_user_by_email(email)
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not user["is_active"]:
        raise HTTPException(status_code=400, detail="User is inactive")
    
    token_data = {
        "sub": user["email"],
        "role": user["role"]
    }
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "role": user["role"]
    }

@app.get("/api/users/me", response_model=User)
async def get_current_user(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user = get_user_by_email(payload["sub"])
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: int, token: str):
    # Verify admin role
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload["role"] != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = next((user for user in users_db if user["id"] == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
