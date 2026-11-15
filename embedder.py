# Превращаем текст в вектор через sentence_transformers
import logging

from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE

logger = logging.getLogger(__name__)

# модель грузим только один раз, когда она первый раз понадобится
_model = None


def _get_model():
    global _model
    if _model is None:
        logger.info("Загрузка модели эмбеддингов: %s", EMBEDDING_MODEL)
        _model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Модель загружена, размерность: %d",
                    _model.get_sentence_embedding_dimension())
    return _model


def embed(text):
    """Вектор для одного текста (нормализованный)."""
    model = _get_model()
    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()


def embed_batch(texts, batch_size=EMBEDDING_BATCH_SIZE):
    """Векторы для списка текстов сразу."""
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    logger.debug("Посчитано эмбеддингов: %d", len(texts))
    return [v.tolist() for v in vectors]