import os
from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseEnumeration
import re

class UploadController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024  # Convert MB to bytes
           # Inherited from BaseController


    def validate_file(self, file: UploadFile):
        # Validate file type
        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, ResponseEnumeration.INVALID_FILE_TYPE.value.format(file_type=file.content_type)
        
        # Validate file size
        if file.size is not None and file.size > self.app_settings.MAX_FILE_SIZE * self.size_scale:
            return False, ResponseEnumeration.FILE_TOO_LARGE.value.format(file_size=self.app_settings.MAX_FILE_SIZE)
        
        return True, ResponseEnumeration.FILE_VALIDATION_SUCCESS.value
    
    def generate_unique_filename(self, original_filename: str, project_id: str):
        
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id)

        cleaned_file_name = self.get_clean_file_name(original_filename)

        new_file_location = os.path.join(project_path, f"{random_key}_{cleaned_file_name}")

        while os.path.exists(new_file_location):
            random_key = self.generate_random_string()
            new_file_location = os.path.join(project_path, f"{random_key}_{cleaned_file_name}")
        
        return new_file_location,f"{random_key}_{cleaned_file_name}"
    
    def get_clean_file_name(self, orig_file_name: str):

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name