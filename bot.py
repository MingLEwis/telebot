app.run()
from telegram import Update, ChatPermissions, BotCommand, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, ContextTypes, MessageHandler
from telegram.error import BadRequest
from telegram.helpers import mention_html
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a'
)

logger = logging.getLogger(__name__)


# Hàm khởi tạo lệnh /start
async def start(update, context):
    user = update.message.from_user
    username = user.username if user.username else "Không có username"
    await update.message.reply_text(f'Chào @{username}, tôi là bot Tiểu Ming rất vui được làm quen!')

async def banudid(update, context):
    await update.message.reply_text(
        'Thuật ngữ “ban udid” và “unban” xuất hiện khoảng hơn một năm trước, nhưng trở nên phổ biến khoảng hai năm nay.\n'
        'Chứng chỉ miễn phí là chứng chỉ doanh nghiệp, có thể bị rò rỉ hoặc mua từ chợ đen. Khi sử dụng, không cung cấp thông tin gì đến máy chủ Apple nên không bị cấm, chỉ khi thu hồi quá nhiều thì bị BLACKLIST.\n'
        'Nếu dùng chứng chỉ cá nhân bị Apple thu hồi, sẽ không bị cấm nhưng thời gian duyệt UDID có thể kéo dài 14-30 ngày.'
    )

def get_news():
    list_news = []
    r = requests.get("https://vnexpress.net/")
    soup = BeautifulSoup(r.text, 'html.parser')
    mydivs = soup.find_all("h3", {"class": "title-news"})

    for new in mydivs[:5]:
        newdict = {}
        link = urljoin("https://vnexpress.net/", new.a.get('href'))
        title_with_link = f'<a href="{link}">{new.a.get("title")}</a>'
        newdict["title"] = title_with_link
        list_news.append(newdict)

    return list_news

async def news(update, context):
    data = get_news()
    for item in data:
        await update.message.reply_html(item["title"])

# Hàm kiểm tra quyền admin
async def is_admin(update: Update, user_id: int) -> bool:
    chat_id = update.effective_chat.id
    member = await update.effective_chat.get_member(user_id)
    return member.status in ['administrator', 'creator']

# Hàm thực thi lệnh mute
async def mute(update, context):
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

# Hàm thực thi lệnh unmute
def extract_username(text):
        username_regex = r"@(\w+)"
        match = re.search(username_regex, text)
        if match:
            return match.group(1)
        return None

async def unmute(update, context):
    user = update.effective_user
    if not await is_admin(update, user.id):
        await update.message.reply_text('Bạn cần quyền admin để thực hiện lệnh này.')
        return
    
    message_text = update.message.text
    username = extract_username(message_text)
    if username is None:
        await update.message.reply_text("Vui lòng cung cấp @username.")
        return
    
    chat_id = update.message.chat_id
    try:
        members = await context.bot.get_chat_administrators(chat_id)
        user_id = None
        for member in members:
            if member.user.username.lower() == username.lower():
                user_id = member.user.id
                break

        if user_id is None:
            await update.message.reply_text("Không tìm thấy username.")
            return
        
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            )
        )
        await update.message.reply_text(f'Đã bỏ mute cho @{username}')
    except Exception as e:
        await update.message.reply_text(f'Lỗi: {e}')

# Hàm thực thi lệnh ban
async def ban(update, context):
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
    

# Hàm thực thi lệnh unban
async def unban(update, context):
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

async def set_commands(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Bắt đầu sử dụng bot."),
        BotCommand("news", "Tin tức mới."),
        BotCommand("mute", "Tắt tiếng thành viên."),
        BotCommand("unmute", "Bật tiếng thành viên."),
        BotCommand("ban", "Cấm thành viên."),
        BotCommand("unban", "Bỏ cấm thành viên.")
    ])
    
def main() -> None:

    app = ApplicationBuilder().token("7416926704:AAFa4a34XuPaFijKTRNCapb75yyaRoUnf3c").build()

    # Đăng ký lệnh
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("banudid", banudid))

    app.run_polling()

    app.start()
    app.updater.start_polling()
    app.updater.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
