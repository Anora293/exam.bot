# Строим, сохраняем, загружаем векторы и ищем по ним
import os
import json
import logging

import config
from .corpus import prepare_corpus
from .embedder import embed, embed_batch

logger = logging.getLogger(__name__)


def build_vectors(chunks):
    """Считает вектора для всех чанков."""
    if not chunks:
        logger.warning("Корпус пустой - векторы не построены")
        return []

    texts = [c["text"] for c in chunks]
    logger.info("Строим эмбеддинги для %d чанков...", len(texts))
    vectors = embed_batch(texts)

    result = []
    for chunk, vec in zip(chunks, vectors):
        result.append({
            "id": chunk["id"],
            "source": chunk["source"],
            "text": chunk["text"],
            "vector": vec,
        })
    logger.info("Построено векторов: %d", len(result))
    return result


def save_vectors(vectors, path=config.VECTOR_FILE):
    """Сохраняет векторы в json."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(vectors, f, ensure_ascii=False, indent=2)
        logger.info("Векторы сохранены в %s (%d шт.)", path, len(vectors))
    except IOError as e:
        logger.error("Ошибка сохранения векторов: %s", e)


def load_vectors(path=config.VECTOR_FILE):
    """Загружает векторы из json."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            vectors = json.load(f)
        logger.info("Векторы загружены из %s (%d шт.)", path, len(vectors))
        return vectors
    except (IOError, json.JSONDecodeError) as e:
        logger.error("Ошибка загрузки векторов: %s", e)
        return []


def build_and_save():
    """Корпус -> эмбеддинги -> сохранение."""
    chunks = prepare_corpus()
    vectors = build_vectors(chunks)
    save_vectors(vectors)
    return vectors


def get_or_build_vectors():
    """Если файл с векторами есть - загружаем, если нет - строим."""
    if os.path.exists(config.VECTOR_FILE):
        return load_vectors()
    logger.info("Файла с векторами нет - строим заново")
    return build_and_save()


def cosine_similarity(a, b):
    """Векторы уже нормализованы, поэтому косинус = скалярное произведение."""
    total = 0
    for x, y in zip(a, b):
        total += x * y
    return total


def search(query, vectors, top_k=config.TOP_K, min_score=config.MIN_SIMILARITY):
    """Ищет top_k самых похожих чанков, у которых похожесть больше min_score."""
    q_vec = embed(query)

    scored = []
    for item in vectors:
        score = cosine_similarity(q_vec, item["vector"])
        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)

    result = []
    for score, item in scored[:top_k]:
        if score > min_score:
            result.append(item)

    logger.debug("Поиск '%s': найдено %d чанков (порог=%.2f)",
                 query[:50], len(result), min_score)
    return result