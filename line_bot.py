# line_bot.py
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from database import users, add_user, get_user
from football_api import fetch_competitions, fetch_live_matches, fetch_standings, fetch_matches_by_date, fetch_all_matches
from datetime import datetime, timedelta
import pytz


line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def handle_text_message(event):
    user_id = event.source.user_id
    text = event.message.text

    print(f"Handling text message: {text}")

    user = get_user(user_id)

    # ตรวจสอบว่าผู้ใช้มีสถานะลงทะเบียนหรือไม่
    if user and user.get('registered'):
        # ถ้าข้อความไม่ได้เริ่มต้นด้วย "/" แสดงว่ามันเป็นการเลือกลีก
        if not text.startswith('/'):
            print("Handling league selection")
            handle_league_selection(user_id, text)
            return

    if text.startswith('/ผลบอลสด'):
        print("Handling live scores command")
        handle_live_scores_command(user_id, text)
    elif text.startswith('/ลีค'): #Success
        print("Handling competitions command")
        handle_competitions_command(user_id)
    elif text.startswith('/ตารางคะแนน'): #Success
        print("Handling standings command")
        handle_standings_command(user_id, text)
    elif text.startswith('/ผลบอล'): #Success
        print("Handling scores command")
        handle_scores_command(user_id, text)
    elif text.startswith('/ตารางแข่งขัน'): #Success
        print("Handling schedule command")
        handle_schedule_command(user_id, text)
    elif text.startswith('/ลงทะเบียน'):
        print("Handling register command")
        handle_register_command(user_id)
    else:
        reply_text = "ขออภัย ฉันไม่เข้าใจคำสั่ง ลองใช้คำสั่งเหล่านี้:\n"
        reply_text += "/ผลบอลสด\n"
        reply_text += "/ผลบอล <ชื่อย่อลีก> <วันที่>\n"
        reply_text += "/ลีค\n"
        reply_text += "/ตารางคะแนน <ชื่อย่อลีก>\n"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

def handle_register_command(user_id):
    add_user(user_id)
    competitions = fetch_competitions()
    reply_text = "กรุณาเลือกลีคในการรับการแจ้งเตือน:\n"
    for comp in competitions['competitions']:
        reply_text += f"{comp['name']} | {comp['code']}\n"
    line_bot_api.push_message(user_id, TextSendMessage(text=reply_text))

def handle_league_selection(user_id, text):
    leagues = text.split(',')
    update_user_leagues(user_id, leagues)
    reply_text = "การลงทะเบียนเสร็จสิ้น คุณจะได้รับการแจ้งเตือนจากลีคที่คุณเลือกทุกวัน เวลา 13:00 น."
    line_bot_api.push_message(user_id, TextSendMessage(text=reply_text))

def handle_live_scores_command(user_id, text):
    # บันทึกข้อมูลผู้ใช้ที่ลงทะเบียน
    add_user(user_id)
    args = text.split(' ')
    if len(args) > 1:
        league_name = args[1]
        competitions = fetch_competitions()
        print(f"Competitions: {competitions}")  # Log competitions data
        competition_id = None
        for comp in competitions['competitions']:
            if comp['name'] == league_name:
                competition_id = comp['id']
                break

        if competition_id:
            live_matches = fetch_live_matches(competition_id)
            print(f"Live matches: {live_matches}")  # Log live matches data
            reply_text = create_live_scores_message(live_matches)
        else:
            reply_text = "ขออภัย ไม่พบลีกที่คุณต้องการ"
    else:
        live_matches = fetch_live_matches()
        print(f"Live matches: {live_matches}")  # Log live matches data
        reply_text = create_live_scores_message(live_matches)

    line_bot_api.push_message(user_id, TextSendMessage(text=reply_text))

def create_live_scores_message(live_matches):
    message = "ผลบอลสด:\n"
    for match in live_matches['matches']:
        message += f"{match['homeTeam']['name']} {match['score']['fullTime']['homeTeam']} - {match['score']['fullTime']['awayTeam']} {match['awayTeam']['name']}\n"
    print(f"Live scores message: {message}")  # Log live scores message
    return message

def handle_competitions_command(user_id):
    competitions = fetch_competitions()
    reply_text = "ลีกทั้งหมด:\n"
    for comp in competitions['competitions']:
        reply_text += f"{comp['name']} | {comp['code']}\n"
    line_bot_api.push_message(user_id, TextSendMessage(text=reply_text))

def handle_standings_command(user_id, text):
    args = text.split(' ')
    if len(args) > 1:
        league_code = args[1]
        competitions = fetch_competitions()
        competition_id = None
        for comp in competitions['competitions']:
            if comp['code'] == league_code:
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

def handle_scores_command(user_id, text):
    args = text.split(' ')
    league_code = args[1] if len(args) > 1 else None
    date_str = args[2] if len(args) > 2 else None

    if date_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print(f"Failed to parse date: {date_str}")  # Add this line
            reply_text = "รูปแบบวันที่ไม่ถูกต้อง กรุณาใช้รูปแบบ YYYY-MM-DD"
            line_bot_api.push_message(user_id, TextSendMessage(text=reply_text))
            return
    else:
        date = datetime.now() - timedelta(days=1)  # Use yesterday's date if none provided

    if league_code:
        competitions = fetch_competitions()
        competition_id = None
        for comp in competitions['competitions']:
            if comp['code'] == league_code:
                competition_id = comp['id']
                break

        if competition_id:
            matches = fetch_matches_by_date(competition_id, date)
            reply_text = create_scores_message(matches)
        else:
            reply_text = "ขออภัย ไม่พบลีกที่คุณต้องการ"
    else:
        reply_text = handle_all_leagues_scores(date)

    line_bot_api.push_message(user_id, TextSendMessage(text=reply_text))

def handle_all_leagues_scores(date):
    competitions = fetch_competitions()
    all_matches = []
    for comp in competitions['competitions']:
        matches = fetch_matches_by_date(comp['id'], date)
        all_matches.extend(matches['matches'])
    return create_scores_message({'matches': all_matches})

def create_scores_message(matches_data):
    matches = matches_data["matches"]
    if len(matches) == 0:
        return "ไม่มีการแข่งขันในวันนี้"

    message = ""
    for match in matches:
        message += f"เจ้าบ้าน {match['homeTeam']['name']} {match['score']['fullTime']['home']} - {match['score']['fullTime']['away']} {match['awayTeam']['name']} ทีมเยือน\n"

    return message

def handle_schedule_command(user_id, text):
    args = text.split(' ')
    schedule = fetch_all_matches()
    reply_text = create_schedule_message(schedule)
    line_bot_api.push_message(user_id, TextSendMessage(text=reply_text))

def fetch_schedule():
    # แทนที่ด้วยการเรียกใช้ API ที่เหมาะสม
    return fetch_all_matches()

def fetch_schedule_all_leagues():
    # แทนที่ด้วยการเรียกใช้ API ที่เหมาะสม
    return fetch_all_matches()

def create_schedule_message(schedule):
    message = "ตารางการแข่งขัน:\n"
    prev_league_name = None
    for match in schedule['matches']:
        league_name = match['competition']['name']
        if league_name != prev_league_name:
            message += f"\n{league_name}\n"
            prev_league_name = league_name

        utc_date = datetime.strptime(match['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
        thai_date = utc_date.astimezone(pytz.timezone('Asia/Bangkok')).strftime("%Y-%m-%d %H:%M")
        
        message += f"📣เจ้าบ้าน : {match['homeTeam']['name']} vs เยือน : {match['awayTeam']['name']}\n🏟 กำหนดการ {thai_date}\n"
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
