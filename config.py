import os

# ---------- GigaChat ----------
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS","MDFhMGVkZGUtOWE3NC03ODEyLTliYjctZTEwNjllYjM5YmZkOjVlMWYyNGVmLWJhNmMtNDRkMi1iNTNkLWMxNTNlNTRmZGIzMQ==")
GIGACHAT_MODEL = "GigaChat-2"
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"
GIGACHAT_VERIFY_SSL = False

# ---------- Пути ----------
DOCS_DIR = "docs"
VECTOR_FILE = "vectors.json"
HISTORY_FILE = "chat_history.json"
LOG_FILE = "exam_bot.log"

# ---------- RAG ----------
EMBEDDING_MODEL = "sergeyzh/rubert-tiny-sts-v2"
TOP_K = 2
MIN_SIMILARITY = 0.3
EMBEDDING_BATCH_SIZE = 16

# ---------- Калькулятор плана подготовки ----------
STUDY_CONFIG = {
    "repeat_days": 1,          # сколько дней оставляем на повторение
    "min_hours_per_topic": 1,  # меньше часа на тему - слишком мало
    "max_hours_per_day": 10,   # больше 10 часов в день заниматься нельзя
}

# ---------- История ----------
MAX_HISTORY_MESSAGES = 10