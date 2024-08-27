import os
from fastapi import UploadFile, HTTPException
from pathlib import Path

class MediaService:
    def __init__(self, upload_dir: str):
        self.upload_dir = Path(upload_dir)
        # Create the directory if it doesn't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def list_files(self, folder_path: str = '') -> list:
        folder_path = self.upload_dir / folder_path if folder_path else self.upload_dir
        return [file.name for file in folder_path.iterdir() if file.is_file()]

    def list_folders(self, folder_path: str = '') -> list:
        path = self.upload_dir / folder_path if folder_path else self.upload_dir
        if not path.exists() or not path.is_dir():
            raise HTTPException(status_code=404, detail="Folder not found")
        return [folder.name for folder in self.upload_dir.iterdir() if folder.is_dir()]

    def save_file(self, file: UploadFile) -> str:
        file_location = self.upload_dir / file.filename
        with open(file_location, "wb") as buffer:
            buffer.write(file.file.read())
        return str(file_location)
    
    def rename_file(self, old_name: str, new_name: str, folder: str = "") -> None:
        file_path = (self.upload_dir / folder / old_name) if folder else (self.upload_dir / old_name)
        new_file_path = (self.upload_dir / folder / new_name) if folder else (self.upload_dir / new_name)
        if file_path.exists():
            os.rename(file_path, new_file_path)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    
    def move_file(self, filename: str, target_folder: str) -> None:
        file_path = self.upload_dir / filename
        target_path = self.upload_dir / target_folder / filename
        if file_path.exists():
            # Create target folder if it doesn't exist
            target_path.parent.mkdir(parents=True, exist_ok=True)
            os.rename(file_path, target_path)

    def delete_file(self, filename: str) -> None:
        file_path = self.upload_dir / filename
        if file_path.exists():
            os.remove(file_path)
        else:
            raise HTTPException(status_code=404, detail="File not found")
        
    def create_folder(self, folder_name: str) -> None:
        new_folder_path = self.upload_dir / folder_name
        new_folder_path.mkdir(parents=True, exist_ok=True)
    
    def rename_folder(self, old_name: str, new_name: str) -> None:
        folder_path = self.upload_dir / old_name
        new_folder_path = self.upload_dir / new_name
        if folder_path.exists() and folder_path.is_dir():
            os.rename(folder_path, new_folder_path)
        else:
            raise HTTPException(status_code=404, detail="Folder not found")

    def delete_folder(self, folder_name: str) -> None:
        folder_path = self.upload_dir / folder_name
        if folder_path.exists() and folder_path.is_dir():
            # Use rmtree for non-empty folders
            os.rmdir(folder_path)
        else:
            raise HTTPException(status_code=404, detail="Folder not found")