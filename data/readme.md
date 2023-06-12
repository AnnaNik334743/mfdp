# Данные

В данном разделе представлены скрипты для создания датасетов на платформе HuggingFace. 

Так как я не уверен, что можно самостоятельно распространять данные из используемых датасетов, я не прикладываю ссылки на созданные мной копии на HuggingFace.


# Train

На данный момент создано:

| Название  | Продолжительность (часов) | Описание | Ссылка на источник |
| ------------- | ------------- | ------------- | ------------- |
| aanosov/mfdp_sova_part1  | Content Cell  | Content Cell  | Ссылка на источник |
| aanosov/mfdp_sova_part2  | Content Cell  | Content Cell  | Ссылка на источник |
| aanosov/mfdp_golos09  | Content Cell  | Content Cell  | Ссылка на источник |
| aanosov/mfdp_golos2  | Content Cell  | Content Cell  | Ссылка на источник |
| aanosov/mfdp_sova_part3  | Content Cell  | Content Cell  | Ссылка на источник |
| aanosov/mfdp_sova_part5  | Content Cell  | Content Cell  | Ссылка на источник |
| aanosov/mfdp_sova_part7  | Content Cell  | Content Cell  | Ссылка на источник |
| aanosov/common_voice_ru_part1  | Content Cell  | Content Cell  | Ссылка на источник |
| aanosov/common_voice_ru_part2  | Content Cell  | Content Cell  | Ссылка на источник |
|   |   |   |  |
| aanosov/mfdp_youtube_20230523  | Content Cell  | Content Cell  | Ссылка на источник |
| aanosov/mfdp_youtube_20230528  | Content Cell  | Content Cell  |Ссылка на источник |
|   |   |   |  |
| Итого  | X часов  |   | |

1) Датасет aanosov/mfdp_youtube_20230523. 100 часов ютуб видео. 10% выделено в test, 1% размечен вручную
2) Датасет aanosov/mfdp_youtube_20230528. 48 часов ютуб видео. 10% выделено в test
3) Датасет на основе датасета [Sova](https://sova.ai/dataset/)(около 1/2 раздела с аудиокнигами). В тестовой выборке не присутствует. Длительность ~130 часов
4) Датасет на основе датасета  [Golos](https://github.com/sberdevices/golos) (2/9 файлов сегмента Crowd). В тестовой выборке не присутствует. Длительность ~160 часов

Так как я не уверен, что можно самостоятельно распространять данные из используемых датасетов, я не прикладываю ссылки на созданные мной копии на HuggingFace.

Список использованных видео с Youtube можно найти в файле ./huggingface_youtube/used_videos.csv
Для финального обучения модели планируется использовать в несколько раз больше данных.
