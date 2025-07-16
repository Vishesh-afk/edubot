# from flask import session
# import re
# import datetime
# from sheets_service import get_class_by_name, get_homework, get_timetable
# from mistral_fallback import get_mistral_response, is_educational
# import logging
# logging.basicConfig(level=logging.INFO)

# def parse_query(query, user_id):
#     query = query.strip().lower()
#     logging.info(f"User {user_id} query: {query}, session: {session}")
    
#     # Name should already be set by app.py, so proceed with query logic
#     class_name = session.get("class")
#     if not class_name:
#         logging.error(f"No class in session for query: {query}, session: {session}")
#         return "❌ Session error. Please enter your name again."
    
#     if "change name" in query:
#         session.pop("name", None)
#         session.pop("class", None)
#         return "🔄 Okay, please enter your name again."
#     elif "timetable" in query:
#         day_match = re.search(r"for (\w+)", query)
#         day = day_match.group(1).capitalize() if day_match else datetime.datetime.today().strftime('%A')
#         logging.info(f"Fetching timetable for {class_name} on {day}")
#         return get_timetable(class_name, day)
#     elif "homework" in query:
#         date_match = re.search(r"for (\w+)", query)
#         if date_match:
#             day_name = date_match.group(1).capitalize()
#             today = datetime.datetime.today()
#             days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#             if day_name in days:
#                 day_diff = (days.index(day_name) - today.weekday()) % 7
#                 target_date = (today + datetime.timedelta(days=day_diff)).strftime('%Y-%m-%d')
#             else:
#                 target_date = today.strftime('%Y-%m-%d')
#         else:
#             target_date = datetime.datetime.today().strftime('%Y-%m-%d')
#         return get_homework(class_name, target_date)
#     else:
#         answer = get_mistral_response(query)
#         if is_educational(query, answer):
#             logging.info(f"Educational response for {query}: {answer}")
#             return answer
#         logging.info(f"Non-educational query: {query}")
#         return "🤖 Sorry, I can only help with school-related questions like timetable or homework."
from flask import session
import re
import datetime
from sheets_service import get_class_by_name, get_homework, get_timetable
from mistral_fallback import get_mistral_response, is_educational
import logging

logging.basicConfig(level=logging.INFO)

def parse_query(query, user_id, class_name=None):
    query = query.strip().lower()
    
    # Use class_name from parameter or fallback to session
    effective_class = class_name or session.get("class")
    
    logging.info(f"User {user_id} query: {query}, class: {effective_class}")

    if not effective_class:
        logging.error(f"No class found for user {user_id} on query: {query}")
        return "❌ I don't know your class yet. Please tell me your name first."

    # Handle name reset (web only)
    if "change name" in query:
        session.pop("name", None)
        session.pop("class", None)
        return "🔄 Okay, please enter your name again."

    elif "timetable" in query:
        day_match = re.search(r"for (\w+)", query)
        day = day_match.group(1).capitalize() if day_match else datetime.datetime.today().strftime('%A')
        logging.info(f"Fetching timetable for {effective_class} on {day}")
        return get_timetable(effective_class, day)

    elif "homework" in query:
        date_match = re.search(r"for (\w+)", query)
        if date_match:
            day_name = date_match.group(1).capitalize()
            today = datetime.datetime.today()
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if day_name in days:
                day_diff = (days.index(day_name) - today.weekday()) % 7
                target_date = (today + datetime.timedelta(days=day_diff)).strftime('%Y-%m-%d')
            else:
                target_date = today.strftime('%Y-%m-%d')
        else:
            target_date = datetime.datetime.today().strftime('%Y-%m-%d')

        logging.info(f"Fetching homework for {effective_class} on {target_date}")
        return get_homework(effective_class, target_date)

    else:
        answer = get_mistral_response(query)
        if is_educational(query, answer):
            logging.info(f"Educational response for {query}: {answer}")
            return answer
        logging.info(f"Non-educational query: {query}")
        return "🤖 Sorry, I can only help with school-related questions like timetable or homework."
