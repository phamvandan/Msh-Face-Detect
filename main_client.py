
import pika
import json
import os

def recieve(queue_name='hello'):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare a queue (should be the same as the sender)
    channel.queue_declare(queue=queue_name)

    # Define a callback function to process the received message
    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        data = json.loads(body.decode('utf-8'))
        if data["training_status"] == 0:
            print(f"Training {queue_name} finished")
            connection.close()
            return
    # Subscribe the callback function to the queue
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


import requests
# for train
def call_training(train_id="123", model_type="yolon", data_type="face_mask", epochs = 3, batch_size=8):
    url = f"http://localhost:9500/call_train?epochs={epochs}&batch_size={batch_size}&data_type={data_type}&model_type={model_type}&id={train_id}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    print("Start read message from queue, you can use thread here!")
    recieve(queue_name=train_id)
    
# for test
def call_testing(model_type="yolon", data_type="face_mask"):
    url = f"http://localhost:9500/call_test?data_type={data_type}&model_type={model_type}"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
# for infer
def call_infer(model_type="yolon", img_path="/home/optimus/Pictures/2bfb2126-7e38-4192-ac06-c2451a30bfed.Screenshot from 2023-11-30 14-29-35.png"):
    url = f"http://localhost:9500/call_infer?model_type={model_type}"

    payload = {}
    files=[
    ('file',(os.path.basename(img_path),open(img_path,'rb'),'image/png'))
    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.text)


if __name__ == "__main__":
    # ---INFER WITH 3 TYPE OF MODEL---
    # call_infer(model_type="yolon5")
    # call_infer(model_type="yolon")
    # call_infer(model_type="yolos")

    # ---TRAIN WITH 3 TYPE OF MODEL, YOU CAN CHANGE FLEXIBLE---
    # call_training(train_id="123", model_type="yolos", data_type="lfwd")
    # call_training(train_id="123", model_type="yolon", data_type="wild01")
    # call_training(train_id="123", model_type="yolon5", data_type="face_mask")
    
    # ---TEST WITH 3 TYPE OF MODEL, YOU CAN CHANGE FLEXIBLE---
    call_testing(model_type="yolos", data_type="wild01")
    # call_testing(model_type="yolon", data_type="lfwd")
    # call_testing(model_type="yolon5", data_type="face_mask")