from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from datetime import datetime, timedelta

app = Flask(__name__)

# 專題討論的日期和時間
current_time = datetime.now()
seminar_dates_times = [
    (2024, 3, 16, 10, 25),
    (2024, 3, 21, 13, 30),
    (2024, 4, 18, 13, 30),
    (2024, 4, 25, 13, 30),
    (2024, 5,  2, 13, 30),
    (2024, 5, 16, 13, 30),
    (2024, 5, 30, 13, 30),
    (2024, 6,  6, 13, 30)
]


# Channel Access Token
line_bot_api = LineBotApi('U1W/9OQpFT6hzgJt1j5Db+As62WY8bU0vrZbXktTk0ANe5/3p8aZXlrPJPTakdG8goEf5fAwOBO20N9qJhu84+p9m03aHEHzZcB3qopKwPtEyNkJ19ia1vdRdZLxo2dic8/zo4vco3CxiM97Y9/JdAdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('88b153db80219bd2b8cf93737c6c6ef4')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 接收到訊息
    received_message = event.message.text.lower()
    trigger_keywords = ["專題討論", "專討", "seminar"]
    # 如果收到訊息是「專題討論」，則回傳「繳交心得」

    for seminar_date_time in seminar_dates_times:
        year, month, day, hour, minute = seminar_date_time
        seminar_date = datetime(year, month, day, hour, minute)
        # 專討前一小時發送提醒
        if seminar_date - timedelta(minutes=60) == current_time.replace(second=0, microsecond=0):
            reply_message = "今天有專討"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
        # seminar = current 發送url
        elif seminar_date == current_time.replace(second=0, microsecond=0):
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="https://moodle.ncku.edu.tw/course/view.php?id=38673"))
        while seminar_date > current_time:
            # 如果收到訊息是「下次專討」，則回傳下次專討的日期和時間
            if "下次專討" in received_message:
                reply_message = f"下次專討時間: {seminar_date}, 當前時間: {current_time}"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
                break

            # 如果收到訊息是「專題討論」，則回傳「繳交心得」
            elif any(keyword in received_message for keyword in trigger_keywords):
                reply_message = "繳交心得"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))
                line_bot_api.push_message(event.source.user_id, TextSendMessage(text="https://moodle.ncku.edu.tw/course/view.php?id=38673"))
                break
        

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
