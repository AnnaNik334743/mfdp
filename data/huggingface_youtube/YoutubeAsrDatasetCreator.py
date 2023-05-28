import srt
import string
import random
import os
from pydub import AudioSegment
import pandas as pd
import re
from huggingface_hub import login
from datasets import load_dataset
from data.huggingface_youtube.dataset_config import *
from retry import retry
pd.options.mode.chained_assignment = None


class YoutubeAsrDatasetCreator:

    def __init__(self, source_path, target_path, control_path,
                 hf_account, hf_write_token, hf_dataset_name_pattern,
                 test_size, control_size):

        self.source_path = source_path
        self.target_path = target_path
        self.control_path = control_path
        self.hf_account = hf_account
        self.hf_write_token = hf_write_token
        self.hf_dataset_name_pattern = hf_dataset_name_pattern
        self.test_size = test_size
        self.control_size = control_size

        # создаем датафрейм с информацией про все семплы
        # в него будем добавлять датафреймы полученные из функции dataframe_from_youtube_video
        self.df = pd.DataFrame(columns=['file_name', 'split', 'full_path',
                                        'answer', 'duration', 'source', 'start', 'end',
                                        'if_completed'])
        self.df["if_completed"] = self.df["if_completed"].astype(bool)
        if os.path.exists(f'{self.control_path}/metadata.csv'):
            self.df = pd.concat([self.df, pd.read_csv(f'{self.control_path}/metadata.csv')])
        if os.path.exists(f'{self.target_path}/metadata.csv'):
            self.df = pd.concat([self.df, pd.read_csv(f'{self.target_path}/metadata.csv')])
        self.df["if_completed"] = self.df["if_completed"].astype(bool)

        if os.path.exists('created_datasets.csv'):
            self.created_datasets = pd.read_csv('created_datasets.csv')
        else:
            self.created_datasets = pd.DataFrame(columns=['dataset_path', 'length_hours', 'creation_date'])

        if os.path.exists('used_videos.csv'):
            self.used_videos = pd.read_csv('used_videos.csv')
        else:
            self.used_videos = pd.DataFrame(columns=['video', 'length_hours', 'dataset_path'])


    @retry(tries=10)
    def normalize_names(self):
        """
        фунция проходит по всем .mp3 и .srt файлам в папке source
        и оставляет только буквы, цифры и пробелы, а также нормализует количество пробелов
        """

        print()
        print('retry_norm')
        print()
        for filename in os.listdir(self.source_path):
            if filename.endswith(".mp3") or filename.endswith(".srt"):
                current_filename_without_extension = filename[:-4]
                new_filename_without_extension = re.sub("[^0-9A-Za-zА-Яёа-яЁ ]", " ", current_filename_without_extension)
                new_filename_without_extension = " ".join(new_filename_without_extension.split())
                os.rename(os.path.join(self.source_path, f'{current_filename_without_extension}{filename[-4:]}'),
                          os.path.join(self.source_path, f'{new_filename_without_extension}{filename[-4:]}'))

    @retry(tries=10)
    def merge_names(self):
        """
        так как аудио-файлам в качестве имени присваевается название видео
        а файлам-субтитрам в имя добавляется дополнительная информация
        мердж происходит с помощью поиска имени файла .mp3 в именах .srt файлов

        код корявый и не оптимальный, но вряд ли мы за раз будем прогонять десятки тысяч файлов,
        так что это не принципиально
        особенно по сравнению с быстродействием других операций
        """
        for filename_mp3 in os.listdir(self.source_path):
            if filename_mp3.endswith(".mp3"):
                filename_without_extension = filename_mp3[:-4]
                for filename_srt in os.listdir(self.source_path):
                    if filename_srt.endswith(".srt"):
                        if filename_without_extension in filename_srt:
                            os.rename(os.path.join(self.source_path, filename_srt),
                                      os.path.join(self.source_path, f'{filename_without_extension}.srt'))
                if not os.path.exists(os.path.join(self.source_path, f'{filename_without_extension}.srt')):
                    raise RuntimeError(f"MP3-file '{filename_without_extension}.mp3' doesnt have subtitles'")

    @retry(tries=10)
    def __generate_random_filename(self, length=20):
        """
        функция генерирует случайную буквенную последовательность указанной длины
        и проверяет чтобы такое имя уже не использовалось в данном датасете
        """
        letters = string.ascii_lowercase
        rand_filename = ''.join(random.choice(letters) for _ in range(length))
        while os.path.exists(os.path.join(self.target_path, f"{rand_filename}.wav")):
            rand_filename = ''.join(random.choice(letters) for _ in range(length))
        return rand_filename

    @retry(tries=10)
    def __dataframe_from_youtube_video(self, subs, filename_without_extension, stride=-1):

        """
        создаем датафрейм
        дальше идем по файлу, пока можем выбрать кусок длиной 30 секунд - выбираем и
        добавляем соответствующую строку в датафрейм
        по умолчанию stride=-1 - в этом случае аудио
        нарезается без пересечений. Если stride>0, то сэмплы нарезаются внахлест со сдвигом на stride
        чанков субтитров
        с вероятностью test_size сэмпл идет в test
        с вероятностью control_size сэмпл идет в control

        на выходе получаем датафрейм, содержащий информацию для последующей нарезки данного видео
        в нем содержится
        file_name - название сэмпла
        split - train/test/control
        full_path - путь по которому следует поместить сэмпл
        answer - расшифровка сэмлп
        duration - продолжительность в секундах
        source - название видео из которого взят данный сэмпл
        start, end - границы, по которым нужно вырезать сэмпл"""

        df = pd.DataFrame(columns=['file_name', 'split', 'full_path',
                                   'answer', 'duration', 'source', 'start', 'end',
                                   'if_completed'])
        df["if_completed"] = df["if_completed"].astype(bool)

        i = 0
        j = 0

        while (j < len(subs)) and (subs[-1].end - subs[i].start > datetime.timedelta(seconds=30)):

            while subs[j].end - subs[i].start <= datetime.timedelta(seconds=30):
                j += 1

            filename = self.__generate_random_filename()

            random_split = random.random()
            if random_split < self.test_size:
                train_test_control = 'test'
                ttc_path = self.target_path
            elif random_split > (1-self.control_size):
                train_test_control = 'control'
                ttc_path = self.control_path
            else:
                train_test_control = 'train'
                ttc_path = self.target_path

            new_row = pd.DataFrame({'file_name': f'{train_test_control}/{filename}.wav',
                                    'split': train_test_control,
                                    'full_path': rf"{os.path.join(ttc_path, train_test_control, f'{filename}.wav')}",
                                    'answer': (' '.join(chunk.content for chunk in subs[i:j])).strip(),
                                    'duration': subs[j - 1].end.total_seconds() - subs[i].start.total_seconds(),
                                    'source': f'{filename_without_extension}',
                                    'start': subs[i].start.total_seconds(),
                                    'end': subs[j - 1].end.total_seconds(),
                                    'if_completed': False
                                    }, index=[0])

            df = pd.concat([df , new_row], ignore_index=True)

            if stride == -1:
                i = j
                j += 1
            else:
                i += stride

        return df

    @retry(tries=3)
    def unpaking_youtube_folder(self):

        self.normalize_names()
        self.merge_names()

        # создаем папку target, если ее не существует, добавляем в нее папки train, test
        if not os.path.exists(self.target_path):
            os.mkdir(self.target_path)
        if not os.path.exists(os.path.join(self.target_path, 'train')):
            os.mkdir(os.path.join(self.target_path, 'train'))
        if not os.path.exists(os.path.join(self.target_path, 'test')):
            os.mkdir(os.path.join(self.target_path, 'test'))

        # создаем папку control
        if not os.path.exists(self.control_path):
            os.mkdir(self.control_path)
        if not os.path.exists(os.path.join(self.control_path, 'control')):
            os.mkdir(os.path.join(self.control_path, 'control'))

        # далее tt~train/test, c~control
        df_tt_path = os.path.join(self.target_path, 'metadata.csv')
        df_c_path = os.path.join(self.control_path, 'metadata.csv')

        df_to_delete = self.df.loc[~self.df['if_completed']]

        for index, row in df_to_delete.iterrows():
            if os.path.exists(row['full_path']):
                os.remove(row['full_path'])

        self.df = self.df.loc[self.df['if_completed']]

        df_tt = self.df.loc[self.df.split.isin(['test', 'train'])]
        df_tt.drop(columns=['start', 'end', 'split'], inplace=True)
        df_tt.to_csv(df_tt_path, index=False, encoding='utf-8')

        df_c = self.df[self.df.split == 'control']
        df_c.drop(columns=['start', 'end',  'split'], inplace=True)
        df_c.to_csv(df_c_path, index=False, encoding='utf-8')


        for root, dirs, files in os.walk(self.source_path):
            for filename in files:
                if filename.endswith(".mp3"):

                    filename_without_extension = filename[:-4]
                    if filename_without_extension not in self.used_videos['video'].values:

                        print('filename:', filename_without_extension)

                        with open(os.path.join(self.source_path, f"{filename_without_extension}.srt"), "r",
                                  encoding='utf-8') as f:
                            subs_raw = f.read()
                        subs = list(srt.parse(subs_raw))

                        current_video_df = self.__dataframe_from_youtube_video(subs, filename_without_extension)
                        self.df = pd.concat([self.df, current_video_df]).reset_index(drop=True)

                        df_tt = self.df.loc[self.df.split.isin(['test', 'train'])]
                        df_tt.drop(columns=['start', 'end', 'split'], inplace=True)
                        df_tt.to_csv(df_tt_path, index=False, encoding='utf-8')

                        df_c = self.df[self.df.split=='control']
                        df_c.drop(columns=['start', 'end',  'split'], inplace=True)
                        df_c.to_csv(df_c_path, index=False, encoding='utf-8')

                        # получили датафрейм для данного видео. начинаем нарезать
                        pr = os.path.join(self.source_path, f"{filename_without_extension}.mp3")
                        sound = AudioSegment.from_mp3(pr)
                        sound = sound.set_frame_rate(16000)
                        sound = sound.set_channels(1)

                        for index, row in current_video_df.iterrows():
                            sound_trimmed = sound[row['start'] * 1000: row['end'] * 1000]
                            sound_trimmed.export(row['full_path'], format="wav")

                        del sound

                        self.df['if_completed'] = True

                        # добавляем информацию о том, что обработали данное видео
                        self.used_videos.loc[len(self.used_videos)] = [filename_without_extension,
                                                                       round(current_video_df.duration.sum() / 3600, 2),
                                                                       f"{self.hf_account}/{self.hf_dataset_name_pattern}"]

                        # разбиваем общий датафрейм на train/test и control
                        # обновляем на каждом видео, чтобы если что-то сломается можно было начать с того же места
                        df_tt = self.df.loc[self.df.split.isin(['test', 'train'])]
                        df_tt.drop(columns=['start', 'end', 'split'], inplace=True)
                        df_tt.to_csv(df_tt_path, index=False, encoding='utf-8')

                        df_c = self.df[self.df.split == 'control']
                        df_c.drop(columns=['start', 'end', 'split'], inplace=True)
                        df_c.to_csv(df_c_path, index=False, encoding='utf-8')

                        self.used_videos.to_csv('used_videos.csv', index=False, encoding='utf-8')

    @retry(tries=3)
    def create_dataset(self):

        self.dataset = load_dataset("audiofolder", data_dir=self.target_path)
        return self.dataset

    @retry()
    def load_to_huggingface(self):

        # иногда падает, видимо из-за нестабильности интернета, но он понимает если файл был уже загружен
        # поэтому retry работает эффективно
        print()
        print('retry_load')
        print()

        login(token=self.hf_write_token)
        self.dataset.push_to_hub(f"{self.hf_account}/{self.hf_dataset_name_pattern}", private=True)
        df_tt = self.df.loc[self.df.split.isin(['test', 'train'])]
        self.created_datasets.loc[len(self.used_videos)] = [f"{self.hf_account}/{self.hf_dataset_name_pattern}",
                                                            round(df_tt.duration.sum() / 3600, 2),
                                                            datetime.datetime.today().strftime('%Y%m%d')]
        self.created_datasets.to_csv('created_datasets.csv', index=False, encoding='utf-8')


