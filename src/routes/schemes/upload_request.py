from pydantic import BaseModel
from typing import Optional
from fastapi import Path, UploadFile, File

class UploadRequest(BaseModel):
    project_id: int
    file: UploadFile

    @classmethod
    def as_upload(
        cls,
        project_id: int = Path(...),
        file: UploadFile = File(...)
    ):
        return cls(
            project_id=project_id,
            file=file
        )
    
    

