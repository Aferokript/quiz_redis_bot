import os
import random

import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkEventType, VkLongPoll

from procces_quiz_file import get_questions_answers

load_dotenv()

redis_connect = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    db=int(os.environ["REDIS_VK_DB"]),
    decode_responses=True,
)


def vk_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Новый вопрос")
    keyboard.add_button("Сдаться")
    keyboard.add_line()
    keyboard.add_button("Итоговый счет")
    return keyboard


def handle_new_question_request(event, vk_api):
    quiz_data = get_questions_answers()
    quest, answer = random.choice(list(quiz_data.items()))
    user_id = event.user_id
    vk_api.messages.send(user_id=user_id, keyboard=vk_keyboard(), message=quest)
    redis_connect.set(f"user{user_id}:quest", quest)
    redis_connect.set(f"user{user_id}:answer", answer)


def handle_solution_attempt(event, vk_api):
    user_id = event.user_id
    user_answer = event.text
    answer = redis_connect.get(f"user{user_id}:answer")
    if user_answer != answer:
        vk_api.messages.send(
            user_id=user_id,
            keyboard=vk_keyboard(),
            message="Неправильно! Хочешь попробовать еще?",
        )
    else:
        vk_api.messages.send(
            user_id=user_id,
            keyboard=vk_keyboard(),
            message="Поздравляю! Правильный ответ. Для следующего вопроса нажмите на новый вопрос",
        )
        redis_connect.incr(f"user{user_id}:count")


def final_score(event, vk_api):
    user_id = event.user_id
    score = redis_connect.get(f"user{user_id}:count") or 0
    vk_api.messages.send(
        user_id=user_id, keyboard=vk_keyboard(), message=f"Итоговый счет: {score}"
    )


def cancel(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id, keyboard=vk_keyboard(), message="Диалог отменен"
    )


def start(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id, keyboard=vk_keyboard(), message="Бот запущен"
    )


def main():
    vk_bot_token = os.environ["VK_GROUP_TOKEN"]
    vk_session = vk.VkApi(token=vk_bot_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    handlers = {
        "Новый вопрос": handle_new_question_request,
        "Сдаться": cancel,
        "Итоговый счет": final_score,
    }
    for event in longpoll.listen():
        if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
            continue
        handler = handlers.get(event.text, handle_solution_attempt)
        handler(event, vk_api)


if __name__ == "__main__":
    main()
