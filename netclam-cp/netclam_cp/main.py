from handlers.database import get_request_status, get_result, create_request
from handlers.uploads import write_file
from dataclasses_serialization.json import JSONSerializer
from models import request_status
from fastapi import FastAPI, UploadFile, HTTPException
from netclam_cp import version, api_name, file_directory
from typing import Union
import json

api_root = f"/v{version}/{api_name}"

print(api_root)

app = FastAPI()

@app.get(api_root)
async def get_scan(request_id: Union[str, None] = None):
    if request_id == None:
        raise HTTPException(status_code=400, detail="Please provide a request_id in UUID format")
    try:
        status = get_request_status(request_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Request not found.") from exc
    if status == request_status.PENDING:
        return {
            status: request_status.PENDING
        }
    elif status == request_status.COMPLETE:
        try:
            result = get_result(request_id)
        except Exception as exc:
            print(exc)
            raise HTTPException(status_code=404, detail="Result not found.") from exc
        return JSONSerializer.serialize(result)
    
@app.post(api_root)
async def create_scan(file: UploadFile):
    request = create_request(file.filename)
    try:
        write_file(request.id, file)
    except:
        raise HTTPException(status_code=500, detail="An error occurred while storing the file.")
    return JSONSerializer.serialize(request)