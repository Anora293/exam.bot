# Чат-бот: помощник по подготовке к экзамену (вариант 6)

Запуск:
    pip install -r requirements.txt
    export GIGACHAT_CREDENTIALS="ваш_ключ_авторизации"
    python main.py

При первом запуске скачается модель sergeyzh/rubert-tiny-sts-v2,
а векторы сохранятся в vectors.json. Если поменяли файлы в docs/ - удалите vectors.json.
Тестовые вопросы - в test_questions.txt.