import os 
import random
from procces_quiz_file import quiz
from dotenv import load_dotenv
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard
import redis

redis_connect = redis.Redis('localhost', port=6379, db=0, decode_responses=True)


def vk_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос')
    keyboard.add_button('Сдаться')
    
    keyboard.add_line()
    keyboard.add_button('Итоговый счет')
    return keyboard


def handle_new_question_request(event, vk_api):
    quiz_data = quiz()
    quest, answer = random.choice(list(quiz_data.items()))
    user_id = event.user_id
    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=vk_keyboard(),
        message=quest
    )
    redis_connect.set(f'user{user_id}:quest', quest)
    redis_connect.set(f'user{user_id}:answer', answer)
    redis_connect.incr(f'user{user_id}:count')


def handle_solution_attempt(event, vk_api):
    user_id = event.user_id
    user_answer = event.text
    answer = redis.get(f'user{user_id}:answer')
    if user_answer != answer:
        vk_api.messages.send(
            user_id=user_id,
            keyboard=vk_keyboard(),
            message='Неправильно! Хочешь попробовать еще?'
        )
    else:
        vk_api.messages_send(
            user_id=user_id,
            keyboard=vk_keyboard(),
            message='Поздравляю! Правильный ответ. Для следущего вопроса нажмите на новый вопрос'
        )
        redis_connect.set(f'user{user_id}:count', + 1 )


def result(event, vk_api):
    user_id = event.user_id
    result = redis_connect.get(f'user{user_id}: count ')
    vk_api.send_messages(
        user_id=user_id,
        keyboard= vk_keyboard(),
        message=f'Итоговый счет:{result} '
    )


def cancel(event, vk_api):
    vk_api.messages_send(
        user_id = event.user_id,
        keyboard=vk_keyboard(),
        message='Диалог отменен'
    )


def start(event, vk_api):
    vk_api.send_messages(
        user_id=event.user_id,
        keyboard=vk_keyboard(),
        message='Бот запущен'
    )


def main():
    load_dotenv()
    
    vk_bot_token = os.environ['VK_GROUP_TOKEN']
    vk_session = vk.VkApi(token=vk_bot_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                handle_new_question_request(event, vk_api)
                
            elif event.text == 'Сдаться':
                cancel(event, vk_api)
            
            elif event.text == 'Итоговый счет':
                result(event, vk_api)
            
            else:
                handle_solution_attempt(event, vk_api)
                
if __name__ == "__main__":
    main()