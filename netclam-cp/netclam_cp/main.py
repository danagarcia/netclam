from dataclasses_serialization.json import JSONSerializer
from fastapi import FastAPI, UploadFile, HTTPException
from netclam_cp import version, api_name
from netclam_cp.config import Config
from netclam_cp.handler.upload_handler import write_file
from netclam_common.exception import FileNotFoundException, RequestNotFoundException, ResultNotFoundException
from netclam_common.database import create_request, get_file, get_request, get_result
from netclam_common.models.request import COMPLETE
from prometheus_fastapi_instrumentator import Instrumentator
from typing import Union
import uvicorn
from pathlib import Path

config = Config()

apiRoot = f"/v{version}/{api_name}"

app = FastAPI(**config.app)

instrumentator = None if config.metrics['enabled'] is not True \
    else Instrumentator().instrument(app,
            metric_namespace=config.metrics['namespace'],
            metric_subsystem=config.metrics['subsystem'])

@app.get(apiRoot)
async def get_scan(id: Union[str, None] = None):
    if id is None:
        raise HTTPException(status_code=400, detail="Invalid Request ID")
    try:
        request = get_request(id)
        request_json = JSONSerializer.serialize(request)
        request_json['file'] = JSONSerializer.serialize(get_file(id))
        if request.status == COMPLETE:
            request_json['result'] = JSONSerializer.serialize(get_result(id))
        return request_json
    except RequestNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Request Not Found") from exc
    except (FileNotFoundException, ResultNotFoundException) as exc:
        raise HTTPException(status_code=500, detail="Internal Server Error") from exc
    
@app.post(apiRoot)
async def create_scan(file: UploadFile = None):
    if file is None:
        raise HTTPException(status_code=400, detail="Invalid Request: No File Provided")
    try:
        request = create_request()
        write_file(request.id, file)
        return JSONSerializer.serialize(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal Server Error") from exc

@app.on_event("startup")
async def _startup():
    if instrumentator is not None:
        instrumentator.expose(app)

if __name__ == "__main__":
    uvicorn.run("main:app",
        port=config.server['port'],
        log_level=config.server['log_level'])
