# from flask import Flask, render_template, request, send_from_directory, session
# from flask_session import Session
# import os
# from chat_logic import parse_query

# app = Flask(__name__, template_folder='templates')
# app.config["SESSION_TYPE"] = "filesystem"
# app.config["SESSION_PERMANENT"] = False
# Session(app)

# @app.before_request
# def clear_session_on_start():
#     if request.path == '/':
#         if "chat_history" not in session:
#             session["chat_history"] = []
#         # Preserve name and class if they exist
#         name = session.get("name")
#         class_name = session.get("class")
#         session.clear()
#         if name:
#             session["name"] = name
#         if class_name:
#             session["class"] = class_name
#         session["chat_history"] = session.get("chat_history", [])

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
#     logging.info(f"Session at start: {session}")
#     if "chat_history" not in session:
#         session["chat_history"] = []
    
#     if request.method == "POST":
#         user_id = request.remote_addr
#         user_query = request.form.get("query", "").strip().lower()
#         if not user_query:
#             session["chat_history"].append({"text": "❌ Please enter a message.", "is_user": False})
#             return render_template("index.html", chat_history=session["chat_history"])
        
#         session["chat_history"].append({"text": user_query, "is_user": True})
        
#         if not session.get("name") and any(greet in user_query for greet in ["hi", "hello", "hey"]):
#             bot_response = "👋 Hello! Please enter your name to get started."
#         else:
#             bot_response = parse_query(user_query, user_id)
        
#         session["chat_history"].append({"text": bot_response, "is_user": False})
#         return render_template("index.html", chat_history=session["chat_history"])
    
#     return render_template("index.html", chat_history=session["chat_history"])

# if __name__ == "__main__":
#     import logging
#     logging.basicConfig(level=logging.INFO)
#     app.run(debug=True)
from flask import Flask, render_template, request, send_from_directory, session
from flask_session import Session
import os
from sheets_service import get_class_by_name
from chat_logic import parse_query
import logging

app = Flask(__name__, template_folder='templates')
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

@app.before_request
def clear_session_on_start():
    if request.method == 'GET' and request.path == '/':
        session.clear()
        session["chat_history"] = []
        logging.info(f"Session cleared on start: {session}")

@app.after_request
def add_headers(response):
    response.headers['Cache-Control'] = 'public, max-age=3600'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

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
            logging.info(f"Session after empty query: {session}")
            return render_template("index.html", chat_history=session["chat_history"])
        
        session["chat_history"].append({"text": user_query, "is_user": True})
        logging.info(f"Session after adding query: {session}")
        
        # Check for greeting and prompt for name if not set
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
            bot_response = parse_query(user_query, user_id)
        
        session["chat_history"].append({"text": bot_response, "is_user": False})
        logging.info(f"Session before render: {session}")
        return render_template("index.html", chat_history=session["chat_history"])
    
    return render_template("index.html", chat_history=session["chat_history"])

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)