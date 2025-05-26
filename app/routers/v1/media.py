from fastapi import APIRouter, Query, UploadFile, File, HTTPException
from core.media import MediaService
from fastapi import Request

media_router = APIRouter(
    prefix='/media',
    tags=['media']
)
media_service = MediaService(upload_dir="uploads")

@media_router.get('/')
async def get_all(folder_name: str = Query('')):
    try:
        files = media_service.list_files(folder_path=folder_name)
        folders = media_service.list_folders(folder_path=folder_name)
        return {'folders': folders, 'files': files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@media_router.post("/files/upload")
async def upload_file(file: UploadFile = File(...), request: Request = Request):
    try:
        file_path = media_service.save_file(file)
        base_url = f"{request.url.scheme}://{request.url.hostname}"
        full_url = f"{base_url}/uploads/{file.filename}"
        return {"filename": file.filename, "file_path": file_path, "full_url": full_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@media_router.put("/files/rename")
async def rename_file(old_name: str, new_name: str, folder: str = ""):
    try:
        media_service.rename_file(old_name, new_name, folder)
        return {"detail": "File renamed successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@media_router.post("/move")
async def move_file(filename: str, target_folder: str):
    try:
        media_service.move_file(filename, target_folder)
        return {"detail": "File moved successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@media_router.delete("/files/delete/{filename}")
async def delete_file(filename: str):
    try:
        media_service.delete_file(filename)
        return {"detail": "File deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@media_router.post("/folders/create")
async def create_folder(folder_name: str):
    try:
        media_service.create_folder(folder_name)
        return {"detail": "Folder created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@media_router.put("/folders/rename")
async def rename_folder(old_name: str, new_name: str):
    try:
        media_service.rename_folder(old_name, new_name)
        return {"detail": "Folder renamed successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@media_router.delete("/folders/delete/{folder_name}")
async def delete_folder(folder_name: str):
    try:
        media_service.delete_folder(folder_name)
        return {"detail": "Folder deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))