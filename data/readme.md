# Данные

В разделе содержится информация о данных, которые были использованы в ходе работы над проектом.

На платформе HaggingFace были созданы все необходимые датасеты, которые использовались при обучении и валидации модели. Датасеты приватные, токен для доступа к ним не прикладываю, так как не уверен, что такое распространение не будет нарушать авторских прав создателей. 


# Train

| Название  | Продолжительность (часов) | Описание | Ссылка на источник |
| ------------- | ------------- | ------------- | ------------- |
| aanosov/mfdp_sova_part1  | 136.8  | Аудиокниги  | [Sova Dataset](https://github.com/sovaai/sova-dataset) |
| aanosov/mfdp_sova_part2  | 161.2  | Аудиокниги  | [Sova Dataset](https://github.com/sovaai/sova-dataset) |
| aanosov/mfdp_golos09  | 161  | Речь, похожая на запросы к голосову ассистенту  | [Sber Golos](https://github.com/sberdevices/golos) |
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
| Итого  | 1249 часов  |   | |

* Список использованных видео с Youtube можно найти в файле ./huggingface_youtube/used_videos.csv


# Test

| Название  | Продолжительность (часов) | Описание | Ссылка на источник |
| ------------- | ------------- | ------------- | ------------- |
| aanosov/sova_test  | Content Cell  | Аудиокниги  | [Sova Dataset](https://github.com/sovaai/sova-dataset) |
| aanosov/golos_test  | Content Cell  | Речь, похожая на запросы к голосову ассистенту  | [Sber Golos](https://github.com/sberdevices/golos) |
| aanosov/asr_calls  | Content Cell  | Телефонные звонки  | [Russian Open Speech To Text (STT/ASR) Dataset](https://github.com/snakers4/open_stt) |
| aanosov/common_voice_ru_test  | 4.3  | Краудсорсинговый проект Мозилы, всё, включая текст предложений собирается пользователями  | [Mozilla. Common Voice](https://commonvoice.mozilla.org/en/datasets) |
|   |   |   |  |
| aanosov/youtube_control_001  | 1  | На основе субтитров Youtube, разметка доработана вручную  | Собрано самостоятельно |
| aanosov/habr_toloka_001  | 48.0  | Предложения, содержащие термины. На основе Хабр  | Собрано самостоятельно |


