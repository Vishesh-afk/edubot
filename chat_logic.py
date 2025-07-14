# from datetime import datetime
# from sheets_service import get_homework, get_timetable
# import re

# def parse_query(user_input):
#     user_input = user_input.lower()
#     today_date = datetime.now().strftime("%Y-%m-%d")
#     today_day = datetime.now().strftime("%A")

#     intent = ""
#     class_ = ""
#     section = ""

#     # Detect intent
#     if "homework" in user_input:
#         intent = "homework"
#     elif "timetable" in user_input:
#         intent = "timetable"

#     # Try extracting class and section like '6A', 'class 7B'
#     match = re.search(r'class?\s*(\d{1,2})([a-z])?', user_input)
#     if match:
#         class_ = match.group(1)
#         section = match.group(2) if match.group(2) else "A"
#     else:
#         # Try 6a format
#         match = re.search(r'(\d{1,2})([a-z])', user_input)
#         if match:
#             class_ = match.group(1)
#             section = match.group(2)
#         else:
#             return "Please mention class like '6A' or '7B'."

#     # Get data based on intent
#     if intent == "homework":
#         homework = get_homework(class_, section, today_date)
#         if homework:
#             return "<br>".join(homework)
#         else:
#             return "No homework found for today."

#     elif intent == "timetable":
#         timetable = get_timetable(class_, section, today_day)
#         if timetable:
#             return "<br>".join([f"<b>{p}:</b> {subj}" for p, subj in timetable.items()])
#         else:
#             return "No timetable found for today."

#     return "Please ask for 'homework' or 'timetable' with class like '6A'."
## chat_logic.py
import re
import datetime
from sheets_service import get_class_by_name, get_homework, get_timetable
from mistral_fallback import get_mistral_response, is_educational

# # Store sessions
# user_sessions = {}

# def parse_query(query, user_id):
#     query = query.strip().lower()

#     # Ask name first
#     if user_id not in user_sessions or "name" not in user_sessions[user_id]:
#         user_sessions[user_id] = {"name": query}
#         class_name = get_class_by_name(query)
#         if not class_name:
#             del user_sessions[user_id]
#             return "❌ Name not found. Please enter your correct full name as in records."
#         user_sessions[user_id]["class"] = class_name
#         return f"✅ Hello {query.title()}! You are in class {class_name}. You can now ask for timetable or homework."

#     # Reset name logic
#     if "change name" in query:
#         del user_sessions[user_id]
#         return "🔄 Okay, please enter your name again."

#     # Get user's class
#     class_name = user_sessions[user_id]["class"]

#     # Check for timetable
#     if "timetable" in query:
#         day_match = re.search(r"for (\w+)", query)
#         if day_match:
#             day = day_match.group(1).capitalize()
#         else:
#             day = datetime.datetime.today().strftime('%A')
#         return get_timetable(class_name, day)

#     # Check for homework
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

#     # Fallback to Mistral AI
#     else:
#         answer = get_mistral_response(query)
#         if is_educational(query, answer):
#             return answer
#         return "🤖 Sorry, I can only help with school-related questions like timetable or homework."

from flask import session
import re
import datetime
from sheets_service import get_class_by_name, get_homework, get_timetable
from mistral_fallback import get_mistral_response, is_educational
import logging
logging.basicConfig(level=logging.INFO)

def parse_query(query, user_id):
    query = query.strip().lower()
    logging.info(f"User {user_id} query: {query}, session: {session.get('name')}")
    if "name" not in session:
        session["name"] = query
        class_name = get_class_by_name(query)
        if not class_name:
            session.pop("name", None)
            logging.warning(f"No class found for name: {query}")
            return "❌ Name not found. Please enter your correct full name as in records."
        session["class"] = class_name
        logging.info(f"Set session for {query}: class {class_name}")
        return f"✅ Hello {query.title()}! You are in class {class_name}. You can now ask for timetable or homework."
    if "change name" in query:
        session.pop("name", None)
        session.pop("class", None)
        return "🔄 Okay, please enter your name again."
    class_name = session["class"]
    if "timetable" in query:
        day_match = re.search(r"for (\w+)", query)
        day = day_match.group(1).capitalize() if day_match else datetime.datetime.today().strftime('%A')
        return get_timetable(class_name, day)
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
        return get_homework(class_name, target_date)
    else:
        answer = get_mistral_response(query)
        if is_educational(query, answer):
            logging.info(f"Educational response for {query}: {answer}")
            return answer
        logging.info(f"Non-educational query: {query}")
        return "🤖 Sorry, I can only help with school-related questions like timetable or homework."