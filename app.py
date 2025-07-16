
# from flask import Flask, render_template, request, send_from_directory, session
# from flask_session import Session
# import os
# from sheets_service import get_class_by_name
# from chat_logic import parse_query
# import logging

# app = Flask(__name__, template_folder='templates')
# app.config["SESSION_TYPE"] = "filesystem"
# app.config["SESSION_PERMANENT"] = False
# Session(app)

# @app.before_request
# def clear_session_on_start():
#     if request.method == 'GET' and request.path == '/':
#         session.clear()
#         session["chat_history"] = []
#         logging.info(f"Session cleared on start: {session}")

# @app.after_request
# def add_headers(response):
#     response.headers['Cache-Control'] = 'public, max-age=3600'
#     response.headers['X-Content-Type-Options'] = 'nosniff'
#     return response

# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# @app.route("/", methods=["GET", "POST"])
# def index():
#     logging.info(f"Session at request start: {session}")
#     if "chat_history" not in session:
#         session["chat_history"] = []
    
#     if request.method == "POST":
#         user_id = request.remote_addr
#         user_query = request.form.get("query", "").strip().lower()
#         if not user_query:
#             session["chat_history"].append({"text": "❌ Please enter a message.", "is_user": False})
#             logging.info(f"Session after empty query: {session}")
#             return render_template("index.html", chat_history=session["chat_history"])
        
#         session["chat_history"].append({"text": user_query, "is_user": True})
#         logging.info(f"Session after adding query: {session}")
        
#         # Check for greeting and prompt for name if not set
#         if not session.get("name") and any(greet in user_query for greet in ["hi", "hello", "hey"]):
#             bot_response = "👋 Hello! Please enter your name to get started."
#         elif not session.get("name"):
#             session["name"] = user_query
#             class_name = get_class_by_name(user_query)
#             if not class_name:
#                 session.pop("name", None)
#                 bot_response = "❌ Name not found. Please enter your correct full name as in records."
#             else:
#                 session["class"] = class_name
#                 bot_response = f"✅ Hello {user_query.title()}! You are in class {class_name}. You can now ask for timetable or homework."
#         else:
#             bot_response = parse_query(user_query, user_id)
        
#         session["chat_history"].append({"text": bot_response, "is_user": False})
#         logging.info(f"Session before render: {session}")
#         return render_template("index.html", chat_history=session["chat_history"])
    
#     return render_template("index.html", chat_history=session["chat_history"])

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     app.run(debug=True)
from flask import Flask, render_template, request, send_from_directory, session
from flask_session import Session
import os
from sheets_service import get_class_by_name
from chat_logic import parse_query
import logging

# Twilio WhatsApp Support
from twilio.rest import Client
from dotenv import load_dotenv

# Flask setup
app = Flask(__name__, template_folder='templates')
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

# Load environment variables
load_dotenv()

# Twilio credentials from .env
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
WHATSAPP_FROM = "whatsapp:+14155238886"  # Twilio Sandbox Number
client = Client(TWILIO_SID, TWILIO_AUTH)

# In-memory store for WhatsApp users (per sender number)
whatsapp_user_data = {}

# Clear session on GET /
@app.before_request
def clear_session_on_start():
    if request.method == 'GET' and request.path == '/':
        session.clear()
        session["chat_history"] = []
        logging.info(f"Session cleared on start: {session}")

# Add response headers
@app.after_request
def add_headers(response):
    response.headers['Cache-Control'] = 'public, max-age=3600'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Favicon route
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Main web chatbot route
@app.route("/", methods=["GET", "POST"])
def index():
    logging.info(f"Session at request start: {session}")
    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":
        user_id = request.remote_addr
        user_query = request.form.get("query", "").strip().lower()

        if not user_query:
            session["chat_history"].append({"text": "❌ Please enter a message.", "is_user": False})
            return render_template("index.html", chat_history=session["chat_history"])

        session["chat_history"].append({"text": user_query, "is_user": True})

        # Greeting + Name Prompt
        if not session.get("name") and any(greet in user_query for greet in ["hi", "hello", "hey"]):
            bot_response = "👋 Hello! Please enter your name to get started."
        elif not session.get("name"):
            session["name"] = user_query
            class_name = get_class_by_name(user_query)
            if not class_name:
                session.pop("name", None)
                bot_response = "❌ Name not found. Please enter your correct full name as in records."
            else:
                session["class"] = class_name
                bot_response = f"✅ Hello {user_query.title()}! You are in class {class_name}. You can now ask for timetable or homework."
        else:
            class_name = session.get("class")
            bot_response = parse_query(user_query, user_id, class_name)

        session["chat_history"].append({"text": bot_response, "is_user": False})
        return render_template("index.html", chat_history=session["chat_history"])

    return render_template("index.html", chat_history=session["chat_history"])

# WhatsApp Webhook Route
@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    incoming_msg = request.form.get('Body', '').strip()
    sender = request.form.get('From')  # Format: whatsapp:+919876543210

    logging.info(f"[WhatsApp] Message from {sender}: {incoming_msg}")

    user_info = whatsapp_user_data.get(sender, {})

    if not user_info.get("name") and any(greet in incoming_msg.lower() for greet in ["hi", "hello", "hey"]):
        reply = "👋 Hello! Please enter your full name to get started."
    elif not user_info.get("name"):
        name = incoming_msg.strip().title()
        class_name = get_class_by_name(name)
        if not class_name:
            reply = "❌ Name not found. Please enter your correct full name as in records."
        else:
            user_info["name"] = name
            user_info["class"] = class_name
            whatsapp_user_data[sender] = user_info
            reply = f"✅ Hello {name}! You are in class {class_name}. You can now ask for timetable or homework."
    else:
        user_id = sender
        class_name = user_info.get("class")
        reply = parse_query(incoming_msg, user_id, class_name)

    # Send reply via Twilio
    client.messages.create(
        from_=WHATSAPP_FROM,
        to=sender,
        body=reply
    )

    return "OK", 200

# Run the app
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)
