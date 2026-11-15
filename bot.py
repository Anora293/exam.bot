# Вся логика чат-бота: калькулятор плана, RAG, GigaChat, история диалога
import json
import os
import math
import logging

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

import config
from prompts import SYSTEM_PROMPT, RAG_USER_TEMPLATE, NO_CONTEXT_MESSAGE
from logger_config import setup_logging
from rag import get_or_build_vectors, search

setup_logging()
logger = logging.getLogger(__name__)


class ExamBot:
    """Чат-бот - помощник по подготовке к экзамену (RAG + калькулятор плана)."""

    def __init__(self):
        self.vectors = []
        self.history = []
        logger.info("Инициализация ExamBot")

    # ---------- История ----------
    def _load_history(self):
        if not os.path.exists(config.HISTORY_FILE):
            return []
        try:
            with open(config.HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Не удалось загрузить историю: %s", e)
            return []

    def _save_history(self):
        try:
            with open(config.HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.error("Не удалось сохранить историю: %s", e)

    # ---------- Калькулятор плана подготовки ----------
    def _make_plan(self, topics, days, hours_per_day):
        """Считает, сколько тем в день и сколько часов на тему.
        Возвращает словарь с результатом."""
        cfg = config.STUDY_CONFIG

        study_days = days - cfg["repeat_days"]   # последние дни - на повторение
        if study_days <= 0:
            return None

        topics_per_day = math.ceil(topics / study_days)
        hours_per_topic = hours_per_day / topics_per_day

        return {
            "study_days": study_days,
            "repeat_days": cfg["repeat_days"],
            "topics_per_day": topics_per_day,
            "hours_per_topic": hours_per_topic,
            "total_hours": hours_per_day * days,
        }

    def _run_calculator(self):
        print("--- Калькулятор плана подготовки ---")
        cfg = config.STUDY_CONFIG

        try:
            topics = int(input("Сколько тем нужно выучить: ").strip())
            days = int(input("Сколько дней до экзамена: ").strip())
            hours = float(input("Сколько часов в день можете заниматься: ").strip())
        except ValueError as e:
            logger.error("Некорректный ввод: %s", e)
            print("Некорректный ввод. Нужно вводить числа.\n")
            return

        if topics <= 0 or days <= 0 or hours <= 0:
            print("Все числа должны быть больше нуля.\n")
            return

        if hours > cfg["max_hours_per_day"]:
            print(f"{hours} часов в день - это слишком много, так можно перегореть.")
            print(f"Максимум - {cfg['max_hours_per_day']} часов.\n")
            return

        plan = self._make_plan(topics, days, hours)
        if plan is None:
            print("Времени очень мало - даже на повторение не остаётся.")
            print("Постарайтесь выучить самые важные темы.\n")
            return

        logger.info(
            "Расчёт плана: тем=%d, дней=%d, часов в день=%.1f, тем в день=%d",
            topics, days, hours, plan["topics_per_day"],
        )

        print("\n--- Ваш план ---")
        print(f"Дней на изучение: {plan['study_days']}")
        print(f"Дней на повторение: {plan['repeat_days']}")
        print(f"Тем в день: {plan['topics_per_day']}")
        print(f"Часов на одну тему: {plan['hours_per_topic']:.1f}")
        print(f"Всего часов подготовки: {plan['total_hours']:.0f}")
        if plan["hours_per_topic"] < cfg["min_hours_per_topic"]:
            print("Внимание! На одну тему выходит меньше часа - "
                  "лучше увеличить время занятий.")
        print()

    # ---------- RAG + GigaChat ----------
    def _ask_gigachat_with_rag(self, user_query):
        relevant = search(user_query, self.vectors)
        if relevant:
            parts = []
            for item in relevant:
                parts.append("[" + item["source"] + "] " + item["text"])
            context = "\n".join(parts)
        else:
            context = NO_CONTEXT_MESSAGE

        messages = [Messages(role=MessagesRole.SYSTEM, content=SYSTEM_PROMPT)]

        # добавляем последние сообщения из истории
        for msg in self.history[-config.MAX_HISTORY_MESSAGES:]:
            if msg["role"] == "user":
                role = MessagesRole.USER
            else:
                role = MessagesRole.ASSISTANT
            messages.append(Messages(role=role, content=msg["content"]))

        user_content = RAG_USER_TEMPLATE.format(context=context, question=user_query)
        messages.append(Messages(role=MessagesRole.USER, content=user_content))

        logger.debug("Отправка в GigaChat, сообщений: %d", len(messages))

        with GigaChat(
            credentials=config.GIGACHAT_CREDENTIALS,
            model=config.GIGACHAT_MODEL,
            scope=config.GIGACHAT_SCOPE,
            verify_ssl_certs=config.GIGACHAT_VERIFY_SSL,
        ) as client:
            response = client.chat(Chat(messages=messages))
            answer = response.choices[0].message.content
            logger.info("Ответ GigaChat получен (длина: %d симв.)", len(answer))
            return answer

    # ---------- Чат ----------
    def _run_chat(self):
        print("--- Помощник по подготовке к экзамену (RAG + GigaChat) ---")
        print("Задайте вопрос (или напишите 'выход', чтобы закончить):")

        while True:
            query = input("Вы: ").strip()
            if query.lower() in ("выход", "exit", "quit"):
                logger.info("Завершение по запросу пользователя")
                break
            if not query:
                continue

            logger.info("Запрос: %s", query[:100])

            try:
                answer = self._ask_gigachat_with_rag(query)
                print(f"Бот: {answer}\n")

                self.history.append({"role": "user", "content": query})
                self.history.append({"role": "assistant", "content": answer})
                self._save_history()
                logger.info("История сохранена (%d сообщений)", len(self.history))

            except Exception as e:
                logger.error("Ошибка GigaChat: %s", e, exc_info=True)
                print(f"[Ошибка GigaChat] {e}\n")

    # ---------- Запуск ----------
    def run(self):
        logger.info("Запуск чат-бота")
        print("=" * 50)
        print("Чат-бот: помощник по подготовке к экзамену")
        print("=" * 50)

        logger.info("Загрузка RAG-базы...")
        self.vectors = get_or_build_vectors()
        logger.info("Загружено %d векторов", len(self.vectors))
        print(f"Загружено {len(self.vectors)} векторов.\n")

        self._run_calculator()

        self.history = self._load_history()
        logger.info("Сообщений в истории: %d", len(self.history))

        self._run_chat()

        logger.info("Чат-бот завершил работу")