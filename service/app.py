from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from transformers import pipeline
from pyannote.audio import Pipeline
import torch
import soundfile as sf
import librosa
import uvicorn
from pydub import AudioSegment
import numpy as np
import traceback
import io
import os

if not os.path.exists('whisper_tiny_pipeline'):
    pipe = pipeline('automatic-speech-recognition', model='aanosov/whisper-small', tokenizer='openai/whisper-tiny')
    pipe.save_pretrained('whisper_tiny_pipeline')

app = FastAPI()
templates = Jinja2Templates(directory="templates/")


@app.get('/')
def read_root():
    return 'hello world'

@app.get("/asr")
def form_post(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})

async def file_processing(input_bytes, filename):
    if filename.split('.')[-1] in ['mp3', 'wav', 'm4a', 'aac', 'flac', 'aiff', 'ogg', 'opus', 'webm']:
        audio = AudioSegment.from_file(input_bytes, format=filename.split('.')[-1])
        wav_binary = io.BytesIO()
        audio.export(wav_binary, format="wav")
        wav, sr = librosa.load(wav_binary, sr=16000, mono=True)
        return wav


@app.post("/asr_api")
async def form_post(input_file: UploadFile = File(...), num_speakers: int = Form(...)):
    print(num_speakers)
    input_bytes = io.BytesIO(await input_file.read())
    wav = await file_processing(input_bytes, input_file.filename.split('.')[-1])
    pipe = pipeline('automatic-speech-recognition', 'whisper_tiny_pipeline')
    result = pipe(wav, chunk_length_s=30, generate_kwargs={"language": "<|ru|>", "task": "transcribe"})['text']
    return {'result': f"{result}"}
        # except Exception as e:
        #     return {'error': 'fucking error'}

#     sound = AudioSegment(
#     # raw audio data (bytes)
#     data=await input_file.read(),

#     # 2 byte (16 bit) samples
#     sample_width=2,

#     # 44.1 kHz frame rate
#     frame_rate=44100,

#     # stereo
#     channels=2
# )


# raw_audio_data = sound.raw_data


# b = io.BytesIO()
# audio.export(b, format="wav")

# librosa.load(b)

    # elif input_file.filename.split('.')[-1] in ['webm']:
    #     with open("uploaded_audio.webm", "wb") as file:
    #         file.write(await input_file.read())
    #     audio = AudioSegment.from_file("uploaded_audio.webm", format="webm")
    #     audio.export("uploaded_audio.wav", format="wav")
    #     wav, sr = librosa.load('uploaded_audio.wav', sr=16000, mono=True)
    #     pipe = pipeline('automatic-speech-recognition', 'whisper_pipeline')
    #     result = pipe(wav, generate_kwargs={"language": "<|ru|>", "task": "transcribe", "chunk_length_s": 30, "stride_length_s": 2})
    #     return {'result': result}



if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8080)


# @app.post("/asr")
# def form_post(request: Request, input_file: UploadFile=Form(...)):
#     print(1)
#     if input_file.filename.split('.')[-1] in ['mp3', 'wav']:
#         bytes_audio = input_file.file
#         data, samplerate = sf.read(bytes_audio)
#         pipe = pipeline('automatic-speech-recognition', 'whisper_pipeline')
#         result = pipe(data, generate_kwargs={"language": "<|ru|>", "task": "transcribe"})
#         return templates.TemplateResponse('index.html', context={'request': request, 'result': result['text']})

#     elif input_file.filename.split('.')[-1] in ['mp4', 'm4p', 'avi', 'mov', 'mpeg']:
#         error = f"""К сожалению, на данный момент, платформа поддерживает только файлы в формате 
#         wav и mp3. Ваш файл в формате {input_file.filename.split('.')[-1]}.\n
#         Вы можете конвертировать файл самостоятельно, 
#         воспользовавшись различными онлайн сервисами. Например, https://convertio.co/ru/{input_file.filename.split('.')[-1]}-wav/"""
#         return templates.TemplateResponse('index.html', context={'request': request, 'error': error})

#     elif input_file.filename.split('.')[-1] == '':
#         error = 'Файл не выбран. Попробуйте еще раз.'
#         return templates.TemplateResponse('index.html', context={'request': request, 'error': error})

#     else:
#         error = f"""К сожалению, на данный момент, платформа поддерживает только файлы в формате 
#         wav и mp3. Ваш файл в формате {input_file.filename.split('.')[-1]}."""
#         return templates.TemplateResponse('index.html', context={'request': request, 'error': error})


# def convert_wav_to_numpy_array(filepath):
#     audio_data, sample_rate = sf.read(filepath)
#     audio_array = np.array(audio_data)

#     return audio_array, sample_rate
