import requests
import os 
import re
from telegram.ext import Dispatcher, Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv


quest_and_answer = {}

with open('quiz-questions/1vs1200.txt', 'r', encoding='KOI8-R') as file:
    question = file.read()

question_part = re.split(r'\n\s*\n', question)

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
                quest_and_answer[q_text] = answer   # ← ключ=вопрос, значение=ответ

print('пар:', len(quest_and_answer))
print(quest_and_answer)