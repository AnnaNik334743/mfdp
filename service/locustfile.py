import time
import math
import os
import io
import random
from locust import HttpUser, task, between

TEST_AUDIOS_PATH = '/home/test_audios/'

def generate_request():

    filename=random.choice(os.listdir(TEST_AUDIOS_PATH ))
    filepath = os.path.join(TEST_AUDIOS_PATH, filename)
    with open(filepath, "rb") as f:
        input_file = io.BytesIO(f.read())

    return {
        'input_file': input_file,
        'num_speakers': random.randint(1, 5),
    }


class QuickstartUser(HttpUser):
    wait_time = between(30, 40)

    @task
    def predict(self):

        headers = {
            "Content-Type": "multipart/form-data",
        }

        data = {
            "num_speakers": random.randint(1, 5),
        }

        filename=random.choice(os.listdir(TEST_AUDIOS_PATH ))
        filepath = os.path.join(TEST_AUDIOS_PATH, filename)
        with open(filepath, "rb") as f:
            input_file = f.read()

        files = {
            "input_file": ("file.wav", input_file),
        }

        self.client.post('/asr_api',  data=data, files=files)