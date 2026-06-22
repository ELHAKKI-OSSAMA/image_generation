import os
from uuid import UUID
from fastapi import UploadFile
from typing import Optional
import aiofiles
from pathlib import Path

class StorageService:
    def __init__(self):
        self.upload_dir = Path("uploads/avatars")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_image_types = {"image/jpeg", "image/png", "image/gif"}
        self.max_file_size = 5 * 1024 * 1024  # 5MB

    async def upload_avatar(self, user_id: UUID, file: UploadFile) -> str:
        """Upload a user avatar"""
        # Validate file type
        if file.content_type not in self.allowed_image_types:
            raise ValueError("Invalid file type. Only JPEG, PNG and GIF are allowed")

        # Read file content to check size
        content = await file.read()
        if len(content) > self.max_file_size:
            raise ValueError("File size exceeds maximum allowed (5MB)")

        # Reset file pointer
        await file.seek(0)

        # Generate unique filename
        extension = os.path.splitext(file.filename)[1].lower()
        filename = f"{user_id}{extension}"
        file_path = self.upload_dir / filename

        # Save file
        async with aiofiles.open(file_path, 'wb') as out_file:
            await out_file.write(content)

        # Return public URL
        return f"/avatars/{filename}"

    async def delete_avatar(self, user_id: UUID) -> None:
        """Delete a user's avatar if it exists"""
        for ext in ['.jpg', '.jpeg', '.png', '.gif']:
            file_path = self.upload_dir / f"{user_id}{ext}"
            if file_path.exists():
                file_path.unlink()
                break