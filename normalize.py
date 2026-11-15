import re
import logging

logger = logging.getLogger(__name__)


def normalize_text(text):
    """Делает текст маленькими буквами, убирает знаки препинания, режет на слова."""
    if not text:
        return []
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = text.split()
    logger.debug("Нормализация: получилось %d слов", len(tokens))
    return tokens