from dataclasses_serialization.json import JSONSerializer
from fastapi import FastAPI, HTTPException
from netclam_cp import version, api_name
from netclam_common.exception import FileNotFoundException, RequestNotFoundException, ResultNotFoundException
from netclam_common.database import get_file, get_request, get_result
from netclam_common.models.request import PENDING, COMPLETE
from typing import Union
import uvicorn

apiRoot = f"/v{version}/{api_name}"

app = FastAPI()

@app.get(apiRoot)
async def get_scan(id: Union[str, None] = None):
    if id is None:
        raise HTTPException(status_code=400, detail="Invalid Request ID")
    try:
        request = get_request(id)
        request_json = JSONSerializer.serialize(request)
        request_json['file'] = JSONSerializer.serialize(get_file(id))
        if request.status == PENDING:
            return request_json
        request_json['result'] = JSONSerializer.serialize(get_result(id))
        return request_json 
    except RequestNotFoundException as exc:
        raise HTTPException(status_code=404, detail="Request Not Found") from exc
    except (FileNotFoundException, ResultNotFoundException) as exc:
        raise HTTPException(status_code=500, detail="Internal Server Error") from exc

if __name__ == "__main__":
    uvicorn.run("main:app", port=8080, log_level="info")
