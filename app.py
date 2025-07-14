from flask import Flask, render_template, request, send_from_directory, session
from flask_session import Session
import os
from chat_logic import parse_query

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

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
    if request.method == "POST":
        user_id = request.remote_addr
        user_query = request.form.get("query", "").strip()
        if not user_query:
            return render_template("index.html", chat="❌ Please enter a message.")
        bot_response = parse_query(user_query, user_id)
        return render_template("index.html", chat=bot_response)
    return render_template("index.html", chat="👋 Hi! Please enter your name to get started.")

if __name__ == "__main__":
    app.run(debug=True)