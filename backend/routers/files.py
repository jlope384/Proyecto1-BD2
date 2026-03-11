from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
from bson import ObjectId
from database import fs
import io
from utils.utils import allow_all_cors

router = APIRouter(
    prefix="/files",
    tags=["Files"],
    dependencies=[Depends(allow_all_cors)],
)

@router.options("/{full_path:path}")
def files_cors(full_path: str, response: Response):
    allow_all_cors(response)
    return {"status": "ok"}

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