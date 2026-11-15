# Загружаем документы из папки docs и режем на кусочки (чанки)
import os
import logging

from config import DOCS_DIR

logger = logging.getLogger(__name__)


def load_documents(docs_dir=DOCS_DIR):
    """Читает все .txt файлы из папки. Возвращает список словарей {source, text}."""
    docs = []
    if not os.path.isdir(docs_dir):
        logger.warning("Папка с документами не найдена: %s", docs_dir)
        return docs

    for fname in sorted(os.listdir(docs_dir)):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(docs_dir, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                docs.append({"source": fname, "text": content})
                logger.info("Загружен документ: %s (%d симв.)", fname, len(content))
        except IOError as e:
            logger.error("Ошибка чтения %s: %s", path, e)

    logger.info("Всего документов: %d", len(docs))
    return docs


def split_into_chunks(docs):
    """Один чанк = одна строка документа."""
    chunks = []
    for doc in docs:
        lines = []
        for line in doc["text"].split("\n"):
            line = line.strip()
            if line:
                lines.append(line)
        for i, line in enumerate(lines):
            chunks.append({
                "id": doc["source"] + "_" + str(i),
                "source": doc["source"],
                "text": line,
            })
    logger.info("Получилось чанков: %d", len(chunks))
    return chunks


def prepare_corpus(docs_dir=DOCS_DIR):
    """Загрузка + разбиение на чанки."""
    docs = load_documents(docs_dir)
    return split_into_chunks(docs)