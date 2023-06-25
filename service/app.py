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


if not os.path.exists('whisper_base_pipeline'):
    pipe = pipeline('automatic-speech-recognition', model='openai/whisper-base', tokenizer='openai/whisper-base')
    pipe.save_pretrained('whisper_base_pipeline')


app = FastAPI()
templates = Jinja2Templates(directory="templates/")


@app.get('/')
def read_root():
    return 'hello world'


@app.get("/asr")
def form_post(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})


async def file_processing(input_bytes, filename):
    audio = AudioSegment.from_file(input_bytes, format=filename.split('.')[-1])
    wav_binary = io.BytesIO()
    filepath = 'abc123.wav'
    audio.export(filepath, format="wav")
    return filepath


def one_speaker(filepath):
    wav, sr = librosa.load(filepath, sr=16000, mono=True)
    pipe = pipeline('automatic-speech-recognition', 'whisper_base_pipeline')
    result = pipe(wav, chunk_length_s=30, generate_kwargs={"language": "<|ru|>", "task": "transcribe"})['text']
    return result


def many_speakers(filepath, num_speakers):

    diarization = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                    use_auth_token="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")
    diarization_annotation = diarization(filepath, num_speakers=num_speakers)

    result = f""
    recognition = pipeline('automatic-speech-recognition', 'whisper_base_pipeline')
    wav, sr = librosa.load(filepath, sr=16000, mono=True)
    for segment, track, label in diarization_annotation.itertracks(yield_label=True):
        result = f"{result}{label}, {segment}\n"
        wav_segment = wav[round(segment.start*16000): round(segment.end*16000)]
        recognized_text = recognition(wav_segment, chunk_length_s=30, generate_kwargs={"language": "<|ru|>", "task": "transcribe"})['text']
        result = f"{result}{recognized_text}\n\n"
    return result


@app.post("/asr_api")
async def form_post(input_file: UploadFile = File(...), num_speakers: int = Form(...)):

    try:
        if  input_file.filename.split('.')[-1] in ['mp3', 'wav',  'aac', 'webm']:
            input_bytes = io.BytesIO(await input_file.read())
            filepath = await file_processing(input_bytes, input_file.filename.split('.')[-1])

            if num_speakers==1:
                result = one_speaker(filepath)
            elif (num_speakers>1) and (num_speakers<10):
                result = many_speakers(filepath, num_speakers)
            elif (num_speakers)<1:
                error = f"""Вы ввели количество спикеров меньше 1. Пожалуйста, введите корректное число спикеров."""
                return {'error': error}
            else:
                error = f"""К сожалению, на данный момент мы умеем обрабатывать только аудиозаписи с числом спикеров меньше 10."""
                return {'error': error}
            return {'result': result}

        else:
            error = f"""К сожалению, на данный момент, платформа поддерживает только файлы в формате 
            wav и mp3. Ваш файл в формате {input_file.filename.split('.')[-1]}.\n
            Вы можете конвертировать файл самостоятельно, 
            воспользовавшись различными онлайн сервисами."""
            return {'error': error}
    except:
        error = f"""К сожалению, что-то пошло не так. Проверьте корректность данных или попробуйте еще раз через некоторое время."""
        return {'error': error}


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8080)
