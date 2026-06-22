# AT THE VERY TOP
from schemas.auth import UserResponse, Token
# To this:
from schemas.organization import OrganizationResponse, OrganizationCreate 

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, Union
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import uuid

from core.database import get_db
from database.models import Admin, Organization, OrganizationMember, UserRole
from schemas.auth import (
    TokenData,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)

from dotenv import load_dotenv
import os

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY") # Move to .env in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="postgresql-auth/login")

router = APIRouter(prefix="/postgresql-auth", tags=["PostgreSQL Auth"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Union[Admin, OrganizationMember]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role is None:
            raise credentials_exception
        token_data = TokenData(email=email, role=role)
    except JWTError:
        raise credentials_exception
    
    if token_data.role == UserRole.ADMIN.value:
        user = db.query(Admin).filter(Admin.email == token_data.email).first()
    else:
        user = db.query(OrganizationMember).filter(
            OrganizationMember.email == token_data.email
        ).first()
    
    if user is None:
        raise credentials_exception
    return user

@router.post("/register/admin", response_model=UserResponse)
async def register_admin(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if admin exists
    db_user = db.query(Admin).filter(Admin.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new admin
    hashed_password = get_password_hash(user_data.password)
    db_user = Admin(
        id=uuid.uuid4(),
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=UserRole.ADMIN
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=str(db_user.id),
        email=db_user.email,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        role=db_user.role.value,
        organization_id=None
    )

@router.post("/register/organization", response_model=UserResponse)
async def register_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db)
):
    # Check if organization exists
    db_org_member = db.query(OrganizationMember).filter(
        OrganizationMember.email == org_data.email
    ).first()
    if db_org_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new organization
    org_id = uuid.uuid4()
    db_org = Organization(
        id=org_id,
        name=org_data.organization_name,
        contact_email=org_data.email,
        contact_phone=org_data.phone,
        status='pending'
    )
    
    # Create organization admin user
    hashed_password = get_password_hash(org_data.password)
    db_org_member = OrganizationMember(
        id=uuid.uuid4(),
        organization_id=org_id,
        email=org_data.email,
        password_hash=hashed_password,
        first_name=org_data.first_name,
        last_name=org_data.last_name,
        role=UserRole.ORGANIZATION
    )
    
    db.add(db_org)
    db.add(db_org_member)
    db.commit()
    db.refresh(db_org_member)
    
    return UserResponse(
        id=str(db_org_member.id),
        email=db_org_member.email,
        first_name=db_org_member.first_name,
        last_name=db_org_member.last_name,
        role=db_org_member.role.value,
        organization_id=str(db_org_member.organization_id)
    )

@router.post("/register/user", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(OrganizationMember).filter(
        OrganizationMember.email == user_data.email
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = OrganizationMember(
        id=uuid.uuid4(),
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        organization_id=user_data.organization_id,
        role=UserRole.USER
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=str(db_user.id),
        email=db_user.email,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        role=db_user.role.value,
        organization_id=str(db_user.organization_id)
    )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Try admin login first
    user = db.query(Admin).filter(Admin.email == form_data.username).first()
    if user is None:
        # Try organization member login
        user = db.query(OrganizationMember).filter(
            OrganizationMember.email == form_data.username
        ).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with role information
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Union[Admin, OrganizationMember] = Depends(get_current_user)
):
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role.value,
        organization_id=str(current_user.organization_id) if hasattr(current_user, 'organization_id') else None
    )
