# main.py
from flask import Flask, request, abort
from line_bot import handle_webhook
import logging

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    logging.debug("Received a request")
    handle_webhook(request)
    return "OK", 200

if __name__ == "__main__":
    app.run(port=8080)
