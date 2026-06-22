from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import UserRole, VerificationStatus