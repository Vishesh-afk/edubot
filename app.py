from flask import Flask, render_template, request
from chat_logic import parse_query

app = Flask(__name__)
user_sessions = {}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_id = request.remote_addr  # simple user tracking
        user_query = request.form.get("query", "").strip()

        if not user_query:
            return render_template("index.html", chat="❌ Please enter a message.")

        bot_response = parse_query(user_query, user_id)
        return render_template("index.html", chat=bot_response)

    return render_template("index.html", chat="👋 Hi! Please enter your name to get started.")

if __name__ == "__main__":
    app.run(debug=True)
