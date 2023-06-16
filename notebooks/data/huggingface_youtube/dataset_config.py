import datetime
from data.huggingface_youtube.YoutubeAsrDatasetCreator import YoutubeAsrDatasetCreator

# Paths
SOURCE_PATH = 'source'
TARGET_PATH = 'data'
CONTROL_PATH = 'control'

# HuggingFace
HF_ACCOUNT = 'aanosov'
HF_READ_TOKEN = ""
HF_WRITE_TOKEN = ""
today = datetime.datetime.today().strftime('%Y%m%d')
HF_DATASET_NAME_PATTERN = f"mfdp_youtube_{today}"

# train/test/control split
TEST_SIZE = 0.1
CONTROL_SIZE = 0.0

DatasetCreator = YoutubeAsrDatasetCreator(source_path=SOURCE_PATH, target_path=TARGET_PATH, control_path=CONTROL_PATH,
                             hf_account=HF_ACCOUNT, hf_write_token=HF_WRITE_TOKEN,
                             hf_dataset_name_pattern=HF_DATASET_NAME_PATTERN,
                             test_size=TEST_SIZE, control_size=CONTROL_SIZE)

DatasetCreator.unpaking_youtube_folder()
DatasetCreator.create_dataset()
DatasetCreator.load_to_huggingface()
