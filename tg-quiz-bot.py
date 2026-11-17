import os 
import random
import telegram
import redis
from procces_quiz_file import quiz
from telegram.ext import Dispatcher, Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

redis_connect = redis.Redis('localhost', port=6379, db=0, decode_responses=True)
 

NEW_QUESTION, ANSWER = range(2)
    
    
def main_menu():
    main_keyboard = [
        [
            
            InlineKeyboardButton('Новый вопрос', callback_data='new_question'),
            InlineKeyboardButton('Сдаться', callback_data='give_up'),
            InlineKeyboardButton('Итоговый счет', callback_data='count')
        ]
    ]
   
    return InlineKeyboardMarkup(main_keyboard)


def start(update, context):
    update.message.reply_text("Бот запущен", reply_markup=main_menu())


def handle_new_question_request(update, context):
    update.callback_query.answer()
    quest_and_answers = context.bot_data['quiz']
    quest, answer = random.choice(list(quest_and_answers.items()))
    context.user_data['question'] = quest
    context.user_data['right_answer'] = answer
    update.callback_query.edit_message_text(quest)
    return ANSWER 
    
    
def handle_solution_attempt(update, context):
    user_answer = update.message.text 
    correct_answers = context.user_data.get('right_answer')
    
    if user_answer == correct_answers:
        update.message.reply_text('Поздравляю! Правильный ответ. Для следущего вопроса нажмите на новый вопрос', reply_markup=main_menu())
        return ConversationHandler.END
    else:
        update.message.reply_text('Неправильно! Хочешь попробовать еще?', reply_markup=main_menu())
        return ConversationHandler.END
        

def cancel(update, context):
    update.message.reply_text('Диалог отменен', reply_markup=main_menu())
    return ConversationHandler.END

    
def main():
    load_dotenv()
    
    tg_token = os.environ['TG_TOKEN']
    
    updater = Updater(tg_token, use_context=True)
    telegram_dispatcher = updater.dispatcher
    telegram_dispatcher.bot_data['quiz'] = quiz()
    telegram_dispatcher.add_handler(CommandHandler('start', start))
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handle_new_question_request, pattern='^new_question$')
        ],
        states={
            ANSWER: [
                MessageHandler(Filters.text & ~Filters.command, handle_solution_attempt)
            ],
            
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    telegram_dispatcher.add_handler(conv_handler)
    
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()