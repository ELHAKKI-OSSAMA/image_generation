from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta

from database import get_db
from models.user import User
from database.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")  # Updated token URL to match auth router


from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError

try:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print("SECRET_KEY used:", settings.SECRET_KEY)  # Add this
    print("ALGORITHM used:", settings.ALGORITHM) 
    user_id: str = payload.get("sub")
    if user_id is None:
        logger.error("Token payload missing 'sub' claim.")
        raise credentials_exception
except ExpiredSignatureError:
    logger.error("Token has expired.")
    raise credentials_exception
except JWTClaimsError as e:
    logger.error(f"Invalid claims: {str(e)}")
    raise credentials_exception
except JWTError as e:
    logger.error(f"Signature verification failed or malformed token: {str(e)}")
    raise credentials_exception


# async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
        
#     user = db.query(User).filter(User.id == user_id).first()
#     if user is None:
#         raise credentials_exception
        
#     return user
