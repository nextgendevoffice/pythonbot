# line_bot.py
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from database import users, add_user, get_user
from football_api import fetch_competitions, fetch_live_matches, fetch_standings

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def handle_text_message(event):
    user_id = event.source.user_id
    text = event.message.text

    if text.startswith('/ผลบอลสด'):
        handle_live_scores_command(user_id, text)
    elif text.startswith('/ลีค'):
        handle_competitions_command(user_id)
    elif text.startswith('/ตารางคะแนน'):
        handle_standings_command(user_id, text)
    else:
        reply_text = "ขออภัย ฉันไม่เข้าใจคำสั่ง"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))


def handle_live_scores_command(user_id, text):
    # บันทึกข้อมูลผู้ใช้ที่ลงทะเบียน
    user = get_user(user_id)
    if not user:
        add_user(user_id)
        reply_text = "คุณได้เข้าร่วมแล้ว! ระบบกำลังประมวลผลผลบอลสด...\n\n"
    else:
        reply_text = ""

    args = text.split(' ')
    if len(args) > 1:
        league_name = args[1]
        competitions = fetch_competitions()
        competition_id = None
        for comp in competitions['competitions']:
            if comp['name'] == league_name:
                competition_id = comp['id']
                break

        if competition_id:
            live_matches = fetch_live_matches(competition_id)
            reply_text += create_live_scores_message(live_matches)
        else:
            reply_text += "ขออภัย ไม่พบลีกที่คุณต้องการ"
    else:
        live_matches = fetch_live_matches()
        reply_text += create_live_scores_message(live_matches)

    line_bot_api.push_message(user_id, TextSendMessage(text=reply_text))


def create_live_scores_message(live_matches):
    message = "ผลบอลสด:\n"
    for match in live_matches['matches']:
        message += f"{match['homeTeam']['name']} {match['score']['fullTime']['homeTeam']} - {match['score']['fullTime']['awayTeam']} {match['awayTeam']['name']}\n"
    return message

def handle_competitions_command(user_id):
    competitions = fetch_competitions()
    reply_text = "ลีกทั้งหมด:\n"
    for comp in competitions['competitions']:
        reply_text += f"{comp['name']}\n"

    line_bot_api.push_message(user_id, TextSendMessage(text=reply_text))

def handle_standings_command(user_id, text):
    args = text.split(' ')
    if len(args) > 1:
        league_name = args[1]
        competitions = fetch_competitions()
        competition_id = None
        for comp in competitions['competitions']:
            if comp['name'] == league_name:
                competition_id = comp['id']
                break

        if competition_id:
            standings = fetch_standings(competition_id)
            reply_text = create_standings_message(standings)
        else:
            reply_text = "ขออภัย ไม่พบลีกที่คุณต้องการ"
    else:
        reply_text = "กรุณาระบุชื่อลีกที่คุณต้องการตรวจสอบตารางคะแนน"

    line_bot_api.push_message(user_id, TextSendMessage(text=reply_text))

def create_standings_message(standings):
    message = f"ตารางคะแนน {standings['competition']['name']}:\n"
    for team in standings['standings'][0]['table']:
        message += f"{team['position']}. {team['team']['name']} ({team['points']} คะแนน)\n"
    return message

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    handle_text_message(event)

def handle_webhook(request):
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Check your channel access token/channel secret.")
