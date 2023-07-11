Ниже приведен список созданных датасетов:

# Train

| Название  | Продолжительность (часов) | Описание | Ссылка на источник |
| ------------- | ------------- | ------------- | ------------- |
| aanosov/mfdp_sova_part1  | 136.8  | Аудиокниги  | [Sova Dataset](https://github.com/sovaai/sova-dataset) |
| aanosov/mfdp_sova_part2  | 161.2  | Аудиокниги  | [Sova Dataset](https://github.com/sovaai/sova-dataset) |
| aanosov/mfdp_golos09  | 161  | Речь, похожая на запросы к голосову ассистенту  | [Sber Golos](https://github.com/sberdevices/golos) |
| aanosov/mfdp_golos1  | 120.8  | Речь, похожая на запросы к голосову ассистенту  | [Sber Golos](https://github.com/sberdevices/golos) |
| aanosov/mfdp_golos2  | 113.4  | Речь, похожая на запросы к голосову ассистенту  | [Sber Golos](https://github.com/sberdevices/golos) |
| aanosov/mfdp_golos3  | 99.6  | Речь, похожая на запросы к голосову ассистенту  | [Sber Golos](https://github.com/sberdevices/golos) |
| aanosov/mfdp_golos5  | 113.4  | Речь, похожая на запросы к голосову ассистенту  | [Sber Golos](https://github.com/sberdevices/golos) |
| aanosov/mfdp_golos7  | 109.3  | Речь, похожая на запросы к голосову ассистенту  | [Sber Golos](https://github.com/sberdevices/golos) |
| aanosov/common_voice_ru_part1  | 102.7  | Краудсорсинговый проект Мозилы, всё, включая текст предложений собирается пользователями  | [Mozilla. Common Voice](https://commonvoice.mozilla.org/en/datasets) |
| aanosov/common_voice_ru_part2  | 104.0 | Краудсорсинговый проект Мозилы, всё, включая текст предложений собирается пользователями  | [Mozilla. Common Voice](https://commonvoice.mozilla.org/en/datasets) |
|   |   |   |  |
| aanosov/mfdp_youtube_20230523  | 99.7  | На основе субтитров Youtube *  | Собрано самостоятельно |
| aanosov/mfdp_youtube_20230528  | 48.0  | На основе субтитров Youtube *  | Собрано самостоятельно |
|   |   |   |  |
| Итого  | 1370 часов  |   | |

* Список использованных видео с Youtube можно найти в файле ./huggingface_youtube/used_videos.csv


# Test_cleen

| Название  | Продолжительность (часов) | Описание | Ссылка на источник |
| ------------- | ------------- | ------------- | ------------- |
| aanosov/sova_test  | Content Cell  | Аудиокниги  | [Sova Dataset](https://github.com/sovaai/sova-dataset) |
| aanosov/golos_test  | 7.7  | Речь, похожая на запросы к голосову ассистенту  | [Sber Golos](https://github.com/sberdevices/golos) |
| aanosov/asr_calls  | 11.2  | Телефонные звонки  | [Russian Open Speech To Text (STT/ASR) Dataset](https://github.com/snakers4/open_stt) |
| aanosov/common_voice_ru_test  | 4.3  | Краудсорсинговый проект Мозилы, всё, включая текст предложений собирается пользователями  | [Mozilla. Common Voice](https://commonvoice.mozilla.org/en/datasets) |
|   |   |   |  |
| aanosov/youtube_control_001  | 1  | На основе субтитров Youtube, разметка доработана вручную  | Собрано самостоятельно |




# Test_augmentated

| Название  | Продолжительность (часов) | Описание |
| ------------- | ------------- | ------------- |
| aanosov/sova_test  | Content Cell  |
| aanosov/golos_test  | 7.7  |   | 
| aanosov/asr_calls  | 11.2  |   | 
| aanosov/common_voice_ru_test  | 4.3  |   |
|   |   |   | 
| aanosov/youtube_control_001_aug  | 3  | увеличен в три раза  |

