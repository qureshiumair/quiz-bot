
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if current_question_id == None:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    if not session['test_answer']:
        next_question, next_question_id = get_next_question(
            current_question_id, session)
        bot_responses.append(next_question)
        session["current_question_id"] = next_question_id


    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''

    if current_question_id != None and isinstance(current_question_id, int):
        try:
            answer = int(answer)
            question_info = PYTHON_QUESTION_LIST[current_question_id]
            if answer > len(question_info['options']):
                raise Exception

            if 'answer_map' not in session:
                session['answer_map'] = dict()

            session['answer_map'][current_question_id] = answer-1

        except Exception as err:
            return False, 'KIndly input option number!'

    return True, ""


def get_next_question(current_question_id, session):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''

    if current_question_id == None:
        current_question_id = -1

    question_id = current_question_id + 1
    question_info = PYTHON_QUESTION_LIST[question_id]
    question = f'''Question:{question_info['question_text']}<br>Options:{question_info['options']}'''
    if question_id == len(PYTHON_QUESTION_LIST)-1:
        session['test_answer'] = True

    return question, question_id


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''

    result = ""
    correct_answer = 0
    for i in range(len(PYTHON_QUESTION_LIST)):
        if PYTHON_QUESTION_LIST[i]['answer'] == PYTHON_QUESTION_LIST[i]['options'][session['answer_map'][i]]:
            correct_answer += 1

        result += f'''Question:{PYTHON_QUESTION_LIST[i]['question_text']}<br> correct_answer:{PYTHON_QUESTION_LIST[i]['answer']} <br>your response:{PYTHON_QUESTION_LIST[i]['options'][session['answer_map'][i]]}<br><br>'''

    result += f'''<br>Total score {correct_answer} out of {len(PYTHON_QUESTION_LIST)}'''
    return result
