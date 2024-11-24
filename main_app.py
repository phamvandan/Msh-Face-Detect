from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from main_train import main_train
from main_test import main_test
from main_detect import main_detect
from main_cfg import *
import uvicorn
from threading import Thread
from pathlib import Path
import shutil

UPLOAD_DIRECTORY = Path("./runs/uploaded")
# Ensure the directory exists
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
app = FastAPI()
app.mount("/runs", StaticFiles(directory="./runs"), name="static")


@app.get("/call_train")
def call_train(epochs: int, batch_size: int, data_type: str, model_type: str, id: str):
    # background_tasks.add_task(main_train, epochs, batch_size, data_type, model_type, id)
    Thread(target=main_train, args=(epochs, batch_size, data_type, model_type, id), daemon=True).start()
    return {"status": 200, "message": "success", "data": ""}

@app.get("/call_test")
def call_test(data_type: str, model_type: str):
    data = main_test(data_type=data_type, model_type=model_type)
    return {"status": 200, "message": "success", "data": data}

@app.post("/call_infer")
def call_infer(model_type:str, file: UploadFile = File(...)):
    file_path = UPLOAD_DIRECTORY / file.filename
    # Save the uploaded file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    res_path = main_detect(model_type, str(file_path))
    return {"status": 200, "message": "success", "data": BASE_URL + "/" + res_path}
    
@app.get("/")
def index():
    return {"status": 200, "message": "success", "data": "hello world"}


if __name__ == "__main__":
    uvicorn.run("main_app:app", host="0.0.0.0", port=9500)