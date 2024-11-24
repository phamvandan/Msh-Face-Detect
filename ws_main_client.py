import socketio
import asyncio
import base64
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import socketio
import asyncio
import uvicorn
from contextlib import asynccontextmanager

# Start Socket.IO client in a background task
# connect to websocket server
SOCKET_BACKEND_URL = "http://127.0.0.1:9500"
sio = socketio.AsyncClient()

async def start_client():
    await sio.connect(SOCKET_BACKEND_URL)
    


# Initialize FastAPI app
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    # Connect to the Socket.IO server when FastAPI starts
    await start_client()

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")
    await sio.disconnect()

@sio.event
async def connect():
    print('connection established')

@sio.event
async def receive_training_process(data):
    print("Recieved training results from server:", data)

@sio.event
async def receive_testing_process(data):
    print("Recieved testing results from server:", data)

@sio.event
async def receive_infering_process(data):
    print("Recieved infering results from server:", data)

@sio.event
async def disconnect():
    print('disconnected from server')

# call training
@app.get("/train")
async def trigger_train():
    print('Call training ___________________')
    data = {
        "data_dir": "lfwd", # lfwd / wild01 / face_mask
        "learning_rate": 0.001,
        "epochs": 2,
        "batch_size": 4,
        "val_size": 0.2,
        "embed_size": 128,
        "num_neurons": 512,
        "num_layers": 4,
        "backbone": "yolos", # yolos / yolon / yolon5
        "model_type": "detection",
        "labId": "lab_001",
        "trainId": "train_2024_001"
        }
    await sio.emit('start_training', data=data)
    return 'done'

# call testing face
@app.get("/test")
async def trigger_test():
    print('Call testing ___________________')
    data = {
    "test_data_dir": "lfwd", # lfwd / wild01 / face_mask
    "labId": "lab_002",
    "ckpt_number": 42,
    "model_type": "detection",
    "embed_size": 256,
    "num_neurons": 1024,
    "num_layers": 6,
    "backbone": "yolos", # yolos / yolon / yolon5
    "testId": "test_2024_002"
    }
    await sio.emit('start_testing', data=data)
    return 'done'

# call inference
@app.get("/infer")
async def trigger_infer():
    print('Call inferring ___________________')
    with open("./datasets/lfwd/test/images/512.jpg", "rb") as f:
        file_data = base64.b64encode(f.read()).decode('utf-8')
    data = {
            'model_type': 'yolos', # yolos / yolon / yolon5
            'file_name': '512.jpg',
            'file_data': file_data,
            'labId': '1',
            'inferId': '1'
        }
    # Emit the 'call_infer' event with the model_type and file_data
    await sio.emit('start_infering', data=data)
    return 'done'

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=9600, reload=False)