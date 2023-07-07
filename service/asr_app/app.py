from fastapi import FastAPI, Request, Form, File, UploadFile, Response
from fastapi.templating import Jinja2Templates
import uvicorn

from pydub import AudioSegment
import librosa

from transformers import pipeline 
from pyannote.audio import Pipeline

import os
import sys
import time
import io
import json
import string
import random
import traceback
import logging
from pythonjsonlogger import jsonlogger

from utils import PrometheusMiddleware, metrics


if not os.path.exists('whisper_base_pipeline'):
    pipe = pipeline('automatic-speech-recognition', model='openai/whisper-base', tokenizer='openai/whisper-base')
    pipe.save_pretrained('whisper_base_pipeline')


APP_NAME = os.environ.get("APP_NAME", "app")
EXPOSE_PORT = os.environ.get("EXPOSE_PORT", 8000)

app = FastAPI()
templates = Jinja2Templates(directory="templates/")

app.add_middleware(PrometheusMiddleware, app_name=APP_NAME)
app.add_route("/metrics", metrics)


class EndpointFilter(logging.Filter):
    # Uvicorn endpoint access log filter
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("GET /metrics") == -1

# Filter out /endpoint
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


logger = logging.getLogger(__name__)
logHandler = logging.StreamHandler()

formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d]")

logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)



@app.get('/')
def read_root():
    request_uid = generate_request_uid()
    logger.info({'handler': '/', 'action': 'get_request', 'request_uid': request_uid})
    return 'hello world'


@app.get("/asr")
def form_post(request: Request):
    request_uid = generate_request_uid()
    logger.info({'handler': '/asr', 'action': 'get_request', 'request_uid': request_uid})
    return templates.TemplateResponse('index.html', context={'request': request})


def generate_request_uid():
    """
    функция генерирует случайную буквенную последовательность из 20 символов
    пока нет идентификации пользователей, чтобы разделять логи хотя бы по запросам
    также по этому uid будет называться файл с аудио
    """
    letters = string.ascii_lowercase
    rand_filename = ''.join(random.choice(letters) for _ in range(20))
    return rand_filename

async def file_processing(input_bytes, file_extension, request_uid):
    start_time = time.time()
    audio = AudioSegment.from_file(input_bytes, format=file_extension)
    wav_binary = io.BytesIO()
    filepath = f'{request_uid}.wav'
    audio.export(f'audio_files/{filepath}', format="wav")
    execution_time = time.time() - start_time
    logger.info({'handler': '/asr_api', 'action': 'processing_file_time_logging', 'request_uid': request_uid, 'execution_time': execution_time})
    return filepath


def one_speaker(filepath, request_uid):

    start_time = time.time()
    wav, sr = librosa.load(f'audio_files/{filepath}', sr=16000, mono=True)
    execution_time = time.time() - start_time
    logger.info({'handler': '/asr_api', 'action': 'loading_file_time_logging', 'request_uid': request_uid, 'execution_time': execution_time})
    
    audio_length = len(wav)/16000
    logger.info({'handler': '/asr_api', 'action': 'audio_length_logging', 'request_uid': request_uid, 'audio_length': audio_length})
    
    start_time = time.time()
    pipe = pipeline('automatic-speech-recognition', 'whisper_base_pipeline')
    result = pipe(wav, chunk_length_s=30, generate_kwargs={"language": "<|ru|>", "task": "transcribe"})['text']
    execution_time = time.time() - start_time
    logger.info({'handler': '/asr_api', 'action': 'recognition_time_logging', 'request_uid': request_uid, 'execution_time': execution_time})
    
    return result


def many_speakers(filepath, num_speakers, request_uid):

    start_time = time.time()
    diarization = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                    use_auth_token="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")
    diarization_annotation = diarization(f'audio_files/{filepath}', num_speakers=num_speakers)
    execution_time = time.time() - start_time
    logger.info({'handler': '/asr_api', 'action': 'diarization_time_logging', 'request_uid': request_uid, 'execution_time': execution_time})
    
    wav, sr = librosa.load(f'audio_files/{filepath}', sr=16000, mono=True)
    audio_length = len(wav)/16000
    logger.info({'handler': '/asr_api', 'action': 'audio_length_logging', 'request_uid': request_uid, 'audio_length': audio_length})

    result = f""

    start_time = time.time()
    recognition = pipeline('automatic-speech-recognition', 'whisper_base_pipeline')
    for segment, track, label in diarization_annotation.itertracks(yield_label=True):
        result = f"{result}{label}, {segment}\n"
        wav_segment = wav[round(segment.start*16000): round(segment.end*16000)]
        recognized_text = recognition(wav_segment, chunk_length_s=30, generate_kwargs={"language": "<|ru|>", "task": "transcribe"})['text']
        result = f"{result}{recognized_text}\n\n"
    execution_time = time.time() - start_time
    logger.info({'handler': '/asr_api', 'action': 'recognition_time_logging', 'request_uid': request_uid, 'execution_time': execution_time})

    return result


@app.post("/asr_api")
async def form_post(input_file: UploadFile = File(...), num_speakers: int = Form(...)) -> dict:

    request_uid = generate_request_uid()
    logger.info({'handler': '/asr_api', 'action': 'post_request_logging', 'request_uid': request_uid})

    # try:
    file_extension = input_file.filename.split('.')[-1]
    if  file_extension in ['mp3', 'wav',  'aac', 'webm']:

        logger.info({'handler': '/asr_api', 'action': 'file_extension_logging', 'request_uid': request_uid, "file_extension": file_extension})

        input_bytes = io.BytesIO(await input_file.read())
        filepath = await file_processing(input_bytes, file_extension, request_uid)

        logger.info({'handler': '/asr_api', 'action': 'num_speakers_logging', 'request_uid': request_uid, "num_speakers": num_speakers})

        if num_speakers==1:
            result = one_speaker(filepath, request_uid)
        elif (num_speakers>1) and (num_speakers<10):
            result = many_speakers(filepath, num_speakers, request_uid)
        elif (num_speakers)<1:
            error = f"""Вы ввели количество спикеров меньше 1. Пожалуйста, введите корректное число спикеров."""
            return {'error': error}
        else:
            error = f"""К сожалению, на данный момент мы умеем обрабатывать только аудиозаписи с числом спикеров меньше 10."""
            return {'error': error}
        return {'result': result}


    else:
        logger.error({'handler': '/asr_api', 'action': 'extension_error_logging', 'request_uid': request_uid, "file_extension": file_extension})
        error = f"""К сожалению, на данный момент, платформа поддерживает только файлы в формате 
        wav и mp3. Ваш файл в формате {input_file.filename.split('.')[-1]}.\n
        Вы можете конвертировать файл самостоятельно, 
        воспользовавшись различными онлайн сервисами."""
        return {'error': error}

    # except Exception as ex:
    #     ex_type, ex_value, ex_traceback = sys.exc_info()

    #     # Extract unformatter stack traces as tuples
    #     trace_back = traceback.extract_tb(ex_traceback)

    #     # Format stacktrace
    #     stack_trace = list()

    #     for trace in trace_back:
    #         stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

    #         logger.critical({'handler': '/asr_api', 'action': 'unexpected_error_logging', 'request_uid': request_uid, 
    #         "exception_type": ex_type.__name__,
    #         "exception_message": ex_value,
    #         "exception_trace": stack_trace})

    #     error = f"""К сожалению, что-то пошло не так. Проверьте корректность данных или попробуйте еще раз через некоторое время."""
    #     return {'error': error}


if __name__ == "__main__":
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] — %(message)s"
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] — %(message)s"
    uvicorn.run(app, host='0.0.0.0', port=8000)



