# main.py
from flask import Flask, request, abort
from line_bot import handle_webhook

app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    handle_webhook(request)
    return "OK", 200

if __name__ == "__main__":
    app.run(port=8000)
