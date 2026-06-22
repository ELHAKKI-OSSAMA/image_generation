from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from models.log import Log, LogBase

class InternalLogService:
    """Service for internal logging that bypasses authentication"""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_log(self, log_data: LogBase) -> Optional[Log]:
        """Create a new log entry without authentication"""
        try:
            log_dict = log_data.dict()
            if 'metadata' in log_dict:
                log_dict['log_metadata'] = log_dict.pop('metadata')
            
            db_log = Log(**log_dict)
            self.db.add(db_log)
            await self.db.flush()
            await self.db.commit()
            await self.db.refresh(db_log)
            return db_log
        except Exception:
            await self.db.rollback()
            # Silently fail for internal logging
            return None
