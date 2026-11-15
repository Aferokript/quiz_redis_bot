import os 
import re 
import telegram
import redis
from telegram.ext import Dispatcher, Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

redis_connect = redis.Redis('localhost', port=6379, db=0)
 

NEW_QUESTION, ANSWER = range(2)


def quiz():
    quest_and_answer = {}

    with open('quiz-questions/1vs1200.txt', 'r', encoding='KOI8-R') as file:
        content = file.read()

    question_part = re.split(r'\n\s*\n', content)

    for i, q in enumerate(question_part):
        q = q.strip()
        if not q.lower().startswith('вопрос'):
            continue

        q_text = re.sub(r'^\s*Вопрос\s*\d+\s*:\s*', '', q, flags=re.IGNORECASE).strip()
        q_text = re.sub(r'\s*\n\s*', ' ', q_text).strip()

        if i + 1 < len(question_part):
            nxt = question_part[i + 1].strip()
            if nxt.lower().startswith('ответ'):
                answer = re.sub(r'^\s*Ответ\s*:\s*', '', nxt, flags=re.IGNORECASE).strip()
                answer = re.sub(r'\s*\n\s*', ' ', answer).strip()
                if q_text and answer:
                    quest_and_answer[q_text] = answer

    return quest_and_answer
    
    
def build_main_menu():
    main_keyboard = [
        [
            
            InlineKeyboardButton('Новый вопрос', callback_data='new_question'),
            InlineKeyboardButton('Сдаться', callback_data='give_up'),
            InlineKeyboardButton('Итоговый счет', callback_data='count')
        ]
    ]
   
    return InlineKeyboardMarkup(main_keyboard)
    

def build_try_keyboard():
    new_try = [
            [
                InlineKeyboardButton('Еще раз', callback_data='again')
            ]
     ]
    return InlineKeyboardMarkup(new_try)
 
 
def build_yesnot_keyboard():
    next_question = [
        [
            InlineKeyboardButton('Следующий вопрос', callback_data='next'),
            InlineKeyboardButton('Главное меню', callback_data='main_menu')
        ]
    ]
    return InlineKeyboardMarkup(next_question)


def start(update, context):
    update.message.reply_text("Бот запущен", reply_markup=build_main_menu())


def new_question(update, context):
    quest_and_answers = context.bot_data['quiz']
    all_quests = []
    all_answers = []
    
    for quests, answers in quest_and_answers.items():
        all_quests.append(quests)
        all_answers.append(answers)
    
    user_id = update.effective_user.id
    
    redis.set(f"user:{user_id}:question", all_quests[0])
    update.callback_query.edit_message_text(all_quests[0])
    
    
def check_answer(update, context):
    user_id = update.effective_user.id
    user_answer = update.message.text 
    quest_for_user = redis.get(f'user:{user_id}:question')
    correct_answers = context.bot_data['quiz'][quest_for_user]
    
    if user_answer == correct_answers:
        update.message.reply_text('Поздравляю! Правильный ответ. Для следущего вопроса нажмите на новый вопрос', reply_markup=build_yesnot_keyboard())
    
    else:
        update.message.reply_text('Неправильно! Хочешь попробовать еще?', reply_markup=build_try_keyboard())
    

def reaction_on_input(update, context):
    wait_new_touch = update.callback_query
    
    wait_new_touch.answer()
    
    user_touch = wait_new_touch.data
    
    if user_touch == 'new_question':
        new_question(update, context)
        
    elif user_touch == 'next':
        new_question(update, context)
    
    elif user_touch == 'again':
        new_question(update, context)
        
    

def main():
    load_dotenv()
    
    tg_token = os.environ['TG_TOKEN']
    
    updater = Updater(tg_token, use_context=True)
    telegram_dispatcher = updater.dispatcher
    telegram_dispatcher.bot_data['quiz'] = quiz()
    telegram_dispatcher.add_handler(CommandHandler("start", start))
    telegram_dispatcher.add_handler(CallbackQueryHandler(reaction_on_input))
    telegram_dispatcher.add_handler(CallbackQueryHandler(reaction_on_input))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
