from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from ws_main_train import main_train
from ws_main_test import main_test
from ws_main_detect import main_detect
from main_cfg import *
import uvicorn
from threading import Thread
from pathlib import Path
import socketio
import asyncio
import json
import base64

DEBUG = False
TIMEOUT_LIMIT = 60*60*24
UPLOAD_DIRECTORY = Path("./runs/uploaded")
# Ensure the directory exists
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
app = FastAPI()
app.mount("/runs", StaticFiles(directory="./runs"), name="static")

# initial websocker server
sio = socketio.AsyncServer(async_mode='asgi', logger=DEBUG, engineio_logger=DEBUG)
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


def run_async(func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func(*args))
    loop.close()

async def start_training(data):
    try:
        async def func_with_timeout():
            async for response in main_train(
                data["data_dir"],
                data["learning_rate"],
                data["epochs"],
                data["batch_size"],
                data["val_size"],
                data["embed_size"],
                data["num_neurons"],
                data["num_layers"],
                data["backbone"],
                data["model_type"],
                data["labId"]
            ):
                await sio.emit(
                    "receive_training_process",
                    json.dumps(
                        {
                            "response": response,
                            "labId": data["labId"],
                            "trainId": data["trainId"],
                        }
                    ),
                )
                await asyncio.sleep(0.1)
        # Use asyncio.wait_for to apply the timeout
        await asyncio.wait_for(func_with_timeout(), timeout=TIMEOUT_LIMIT)
    except Exception as e:
        await sio.emit(
            "receive_training_process",
            json.dumps(
                {
                    "response": {
                        "message": str(e),
                        "status": False
                    },
                    "labId": data["labId"],
                    "trainId": data["trainId"],
                }
            ),
        )

async def start_testing(data):
    try:
        async def func_with_timeout():
            response = await main_test(
                data["test_data_dir"],
                data["labId"],
                data["ckpt_number"],
                data["model_type"],
                data["embed_size"],
                data["num_neurons"],
                data["num_layers"],
                data["backbone"],
            )
            await sio.emit(
                f"receive_testing_process",
                json.dumps(
                    {"response": response, "labId": data["labId"], "testId": data["testId"]}
                ),
            )
            await sio.sleep(0.1)

        # Use asyncio.wait_for to apply the timeout
        await asyncio.wait_for(func_with_timeout(), timeout=TIMEOUT_LIMIT)
    except Exception as e:
        await sio.emit(
            "receive_testing_process",
            json.dumps(
                {
                    "response": {
                        "message": str(e),
                        "status": False
                    },
                    "labId": data["labId"],
                    "testId": data["testId"]
                }
            ),
        )

async def start_infering(data):
    try:
        file_path = UPLOAD_DIRECTORY / data["file_name"]
        with file_path.open("wb") as buffer:
            buffer.write(base64.b64decode(data["file_data"]))

        async def func_with_timeout():
            response = await main_detect(
                data["model_type"],
                str(file_path)
            )
            response = BASE_URL + "/" + response
            await sio.emit(
                f"receive_infering_process",
                json.dumps(
                    {"response": response, "labId": data["labId"], "inferId": data["inferId"]}
            ))
            await sio.sleep(0.1)
        await asyncio.wait_for(func_with_timeout(), timeout=TIMEOUT_LIMIT)
    except Exception as e:
        await sio.emit( 
            "receive_infering_process",
            json.dumps(
                {
                    "response": {
                        "message": str(e),
                        "status": False
                    },
                    "labId": data["labId"],
                    "inferId": data["inferId"]
                }
            )
        )
    

# call training ws endpoint
@sio.on("start_training")
async def start_training_listener(sid, data):
    Thread(target=await start_training(data)).start()

# call testing ws endpoint
@sio.on("start_testing")
async def start_testing_listener(sid, data):
    Thread(target=await start_testing(data)).start()

# call infering ws endpoint
@sio.on("start_infering")
async def start_infering_listener(sid, data):
    Thread(target=await start_infering(data)).start()

# Handle connection
@sio.event
async def connect(sid, environ):
    print(f"User connected with session id: {sid}")
    await sio.emit('trigger', '', to=sid)

# Handle disconnection
@sio.event
async def disconnect(sid):
    print(f"User disconnected with session id: {sid}")

@app.get("/")
def index():
    return {"status": 200, "message": "success", "data": "hello world"}

if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=9500)

