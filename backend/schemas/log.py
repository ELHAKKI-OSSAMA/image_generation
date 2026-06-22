from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(str, Enum):
    SYSTEM = "system"
    AUTH = "auth"
    USER = "user"
    ORGANIZATION = "organization"
    EVENT = "event"
    API = "api"


class LogBase(BaseModel):
    level: LogLevel
    category: LogCategory
    message: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Log(LogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class LogFilter(BaseModel):
    level: Optional[List[LogLevel]] = None
    category: Optional[List[LogCategory]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_term: Optional[str] = None


class LogSort(BaseModel):
    field: str = "timestamp"
    ascending: bool = False


class LogPagination(BaseModel):
    page: int = Field(default=1, gt=0)
    per_page: int = Field(default=50, gt=0, le=1000)
