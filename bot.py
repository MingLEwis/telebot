import asyncio
import nest_asyncio
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackContext,
)
from telegram import Update, ChatPermissions, BotCommand
from telegram.error import BadRequest
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os
import random

nest_asyncio.apply()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a'
)

logger = logging.getLogger(__name__)

# Hàm start
async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    username = user.username if user.username else "Không có username"
    await update.message.reply_text(f'Hi @{username}, tôi là bot Tiểu Ming rất vui được làm quen!')

# Hàm blacklist
async def blacklist(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        'Thuật ngữ “ban udid” và “unban” xuất hiện vào khoảng năm 2020, nhưng trở nên phổ biến hơn gần đây.\n'
        'Chứng chỉ miễn phí là chứng chỉ doanh nghiệp, có thể bị rò rỉ hoặc mua từ chợ đen. Khi sử dụng, không cung cấp thông tin gì đến máy chủ Apple nên không bị cấm, chỉ khi thu hồi quá nhiều thì bị BLACKLIST.\n'
        'Nếu dùng chứng chỉ cá nhân bị Apple thu hồi, sẽ không bị cấm nhưng thời gian duyệt UDID có thể kéo dài 14-30 ngày.'
    )

# Hàm lấy tin tức
def get_news():
    list_news = []
    r = requests.get("https://vnexpress.net/")
    soup = BeautifulSoup(r.text, 'html.parser')
    mydivs = soup.find_all("h3", {"class": "title-news"})

    for index, new in enumerate(mydivs[:7], start=1):
        newdict = {}
        link = urljoin("https://vnexpress.net/", new.a.get('href'))
        title_with_link = f'{index}. <a href="{link}">{new.a.get("title")}</a>'
        newdict["title"] = title_with_link
        list_news.append(newdict)

    return list_news

async def news(update: Update, context: CallbackContext) -> None:
    data = get_news()
    news_message = "\n".join([item["title"] for item in data])
    await update.message.reply_html(news_message, disable_web_page_preview=True)

# Hàm kiểm tra admin
async def is_admin(update: Update, user_id: int) -> bool:
    chat_id = update.effective_chat.id
    member = await update.effective_chat.get_member(user_id)
    return member.status in ['administrator', 'creator']

# Hàm random
async def random_keyword(update: Update, context: CallbackContext) -> None:
    question = update.message.text.split("/random", 1)[1].strip()

    keywords = [keyword.strip() for keyword in question.split(",")]

    if len(keywords) >= 2:
        selected_keyword = random.choice(keywords)
        await update.message.reply_text(f'Từ khóa ngẫu nhiên được chọn từ câu hỏi của bạn: {selected_keyword}')
    else:
        await update.message.reply_text('Vui lòng thêm ít nhất 2 từ khoá.')

# Hàm thấy thông tin thời tiết
def get_tt(location):
    api_key = "ca22122a90b399f9e1911fcb43763abd" 
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "q=" + location + "&appid=" + api_key + "&units=metric&lang=vi"
    response = requests.get(complete_url)
    return response.json()

def get_city_name(code):
    cities = {
        "hcm": "Ho Chi Minh City",
        "hn": "Ha Noi",
        "dn": "Da Nang",
        "ct": "Can Tho",
        "hp": "Hai Phong",
        "vt": "Vung Tau",
        "dl": "Da Lat",
        "bd": "Binh Duong",
        "nt": "Nha Trang",
        "pt": "Phan Thiet",
        "hl": "Ha Long"
    }
    return cities.get(code.lower(), code)

async def weather(update: Update, context: CallbackContext) -> None:
    location_code = " ".join(context.args)
    if not location_code:
        await update.message.reply_text("Vui lòng cung cấp mã vùng hoặc tên thành phố.")
        return

    location = get_city_name(location_code)
    weather_data = get_tt(location)
    if weather_data["cod"] == "404":
        await update.message.reply_text(f"Không tìm thấy thông tin thời tiết cho địa điểm: {location}")
        return

    main = weather_data["main"]
    weather = weather_data["weather"][0]
    temp_min = main["temp_min"]
    temp_max = main["temp_max"]
    temp_avg = (temp_min + temp_max) / 2  
    pressure = main["pressure"]
    humidity = main["humidity"]
    wind_speed = weather_data["wind"]["speed"]
    weather_description = weather["description"].capitalize()

    visibility_meters = weather_data.get("visibility", "N/A")
    if visibility_meters != "N/A":
        visibility_kilometers = visibility_meters / 1000  
        visibility_str = f"{visibility_kilometers:.2f} km"
    else:
        visibility_str = "N/A"

    weather_icons = {
        "thermometer": "🌡️", 
        "barometer": "📊", 
        "droplet": "💧", 
        "wind": "🌬️",
        "visibility": "👁️"
    }

    weather_message = (
        f"Tại {location}:\n"
        f"Nhiệt độ trung bình {weather_icons['thermometer']}: {temp_avg:.2f}°C\n"
        f"Áp suất {weather_icons['barometer']}: {pressure} hPa\n"
        f"Độ ẩm {weather_icons['droplet']}: {humidity}%\n"
        f"Tốc độ gió {weather_icons['wind']}: {wind_speed} m/s\n"
        f"Tầm nhìn {weather_icons['visibility']}: {visibility_str}\n"
        f"Mô tả: {weather_description}"
    )

    await update.message.reply_text(weather_message)

# Hàm mute
async def mute(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not await is_admin(update, user.id):
        await update.message.reply_text('Bạn cần quyền admin để thực hiện lệnh này.')
        return

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        user_id = target_user.id
        username = target_user.username
        chat_id = update.message.chat_id
        try:
            await context.bot.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await update.message.reply_text(f'Đã tắt tiếng thành viên @{username}.\nID: {user_id}')
        except BadRequest as e:
            await update.message.reply_text(f'Không thể tắt tiếng thành viên: {e.message}')
    else:
        await update.message.reply_text('Vui lòng trả lời tin nhắn của thành viên bạn muốn tắt tiếng.')

# Hàm unmute
async def unmute(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not await is_admin(update, user.id):
        await update.message.reply_text('Bạn cần quyền admin để thực hiện lệnh này.')
        return

    chat_id = update.message.chat_id
    target_user = None
    user_id = None

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        message_text = update.message.text
        username = extract_username(message_text)
        if username:
            members = await context.bot.get_chat_members(chat_id)
            for member in members:
                if member.user.username.lower() == username.lower():
                    target_user = member.user
                    break

    if target_user:
        user_id = target_user.id
        username = target_user.username
    else:
        await update.message.reply_text(
            "Vui lòng trả lời tin nhắn hoặc cung cấp @username của thành viên bạn muốn bật tiếng."
        )
        return

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        )
        await update.message.reply_text(f'Đã bỏ tắt tiếng thành viên @{username}')
    except Exception as e:
        await update.message.reply_text(f'Lỗi: {e}')

def extract_username(text):
    username_regex = r"@(\w+)"
    match = re.search(username_regex, text)
    if match:
        return match.group(1)
    return None

# Hàm ban
async def ban(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not await is_admin(update, user.id):
        await update.message.reply_text('Bạn cần quyền admin để thực hiện lệnh này.')
        return

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        user_id = target_user.id
        username = target_user.username
        chat_id = update.message.chat_id
        try:
            await context.bot.ban_chat_member(chat_id, user_id)
            await update.message.reply_text(f'Đã cấm thành viên @{username}.')
        except BadRequest as e:
            await update.message.reply_text(f'Không thể cấm thành viên: {e.message}')
    else:
        await update.message.reply_text('Vui lòng trả lời tin nhắn của thành viên bạn muốn cấm.')

# Hàm unban
async def unban(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not await is_admin(update, user.id):
        await update.message.reply_text('Bạn cần quyền admin để thực hiện lệnh này.')
        return

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        user_id = target_user.id
        username = target_user.username
        chat_id = update.message.chat_id
        try:
            await context.bot.unban_chat_member(chat_id, user_id)
            await update.message.reply_text(f'Đã bỏ cấm thành viên @{username}.')
        except BadRequest as e:
            await update.message.reply_text(f'Không thể bỏ cấm thành viên: {e.message}')
    else:
        await update.message.reply_text('Vui lòng trả lời tin nhắn của thành viên bạn muốn bỏ cấm.')

# Khởi tạo lệnh
async def set_commands(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Bắt đầu sử dụng."),
        BotCommand("news", "Tin tức mới."),
        BotCommand("tt", "Thời tiết."),
        BotCommand("mute", "Tắt tiếng thành viên."),
        BotCommand("unmute", "Bật tiếng thành viên."),
        BotCommand("ban", "Cấm thành viên."),
        BotCommand("unban", "Bỏ cấm thành viên."),
        BotCommand("blacklist", "Blacklist iOS."),
        BotCommand("random", "Chọn ngẫu nhiên một từ khóa.")
    ])

async def main():
    application = ApplicationBuilder().token("7416926704:AAFa4a34XuPaFijKTRNCapb75yyaRoUnf3c").build()
# Đăng ký lệnh
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(CommandHandler("tt", weather))
    application.add_handler(CommandHandler("mute", mute))
    application.add_handler(CommandHandler("unmute", unmute))
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CommandHandler("blacklist", blacklist))
    application.add_handler(CommandHandler("random", random_keyword))

    await application.run_polling()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    if loop.is_running():
        nest_asyncio.apply()
        loop.create_task(main())
    else:
        loop.run_until_complete(main())
