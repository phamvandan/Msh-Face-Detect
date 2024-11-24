FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y && apt install build-essential -y
RUN pip install opencv-python pandas matplotlib scipy seaborn loguru thop lab cython cython_bbox shapely uvicorn fastapi python-multipart pika tensorboard aiohttp python-socketio
CMD ["/bin/bash"]