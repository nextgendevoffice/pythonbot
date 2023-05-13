# main.py
from flask import Flask, request, abort
from line_bot import handle_webhook, handle_standings_command, handle_scores_command, handle_schedule_command
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from database import get_all_users, get_followed_leagues

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# กำหนด scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def send_notifications():
    users = get_all_users()  
    for user_id in users:
        followed_leagues = get_followed_leagues(user_id)
        for league in followed_leagues:
            handle_standings_command(user_id, f"/ตารางคะแนน {league}")
            handle_scores_command(user_id, f"/ผลบอล {league}")
            handle_schedule_command(user_id, f"/ตารางแข่งขัน {league}")

# กำหนดงานที่ต้องการเรียกเก็บเวลา
scheduler.add_job(send_notifications, 'cron', hour=13, timezone=pytz.timezone('Asia/Bangkok'))
@app.route("/callback", methods=["POST"])
def callback():
    logging.debug("Received a request")
    handle_webhook(request)
    return "OK", 200

if __name__ == "__main__":
    app.run(port=8080)
