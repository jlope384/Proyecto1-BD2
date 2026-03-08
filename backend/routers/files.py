from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from bson import ObjectId
from database import fs
import io

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_data = await file.read()

    file_id = fs.put(
        file_data,
        filename=file.filename,
        content_type=file.content_type
    )

    return {"file_id": str(file_id)}

@router.get("/{file_id}")
def get_file(file_id: str):
    try:
        grid_out = fs.get(ObjectId(file_id))
    except:
        raise HTTPException(404, "File not found")

    return StreamingResponse(
        io.BytesIO(grid_out.read()),
        media_type=grid_out.content_type
    )