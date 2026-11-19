import re


def get_questions_answers():
    quest_and_answer = {}

    with open("quiz-questions/1vs1200.txt", "r", encoding="KOI8-R") as file:
        content = file.read()

    question_part = re.split(r"\n\s*\n", content)

    for index, questions in enumerate(question_part):
        question = questions.strip()
        if not question.lower().startswith("вопрос"):
            continue

        question_text = re.sub(
            r"^\s*Вопрос\s*\d+\s*:\s*", "", question, flags=re.IGNORECASE
        ).strip()
        question_text = re.sub(r"\s*\n\s*", " ", question_text).strip()

        if index + 1 < len(question_part):
            next_question = question_part[index + 1].strip()
            if next_question.lower().startswith("ответ"):
                answer = re.sub(
                    r"^\s*Ответ\s*:\s*", "", next_question, flags=re.IGNORECASE
                ).strip()
                answer = re.sub(r"\s*\n\s*", " ", answer).strip()
                if question_text and answer:
                    quest_and_answer[question_text] = answer

    return quest_and_answer
