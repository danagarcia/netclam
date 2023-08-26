import os
from fastapi import UploadFile

base_file_directory = "/data"

def create_directory(request_id:str) -> str:
    path = os.path.join(base_file_directory, request_id)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def write_file(request_id:str, file: UploadFile):
    dir_path = create_directory(request_id)
    file_path = os.path.join(dir_path, file.filename)
    if not os.path.exists(file_path):
        with open(file_path, "wb+") as file_stream:
            file_stream.write(file.file.read())