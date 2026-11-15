import logging
import logging.handlers
from config import LOG_FILE


def setup_logging():
    """Настраиваем логи: в консоль INFO, в файл DEBUG."""
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    # чтобы обработчики не добавлялись два раза
    if not root.handlers:
        root.addHandler(console)
        root.addHandler(file_handler)