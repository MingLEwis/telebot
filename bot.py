app.run()
from telegram import Update, ChatPermissions, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import BadRequest
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a'
)

logger = logging.getLogger(__name__)


# Hàm khởi tạo lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Xin chào! Tôi là Tiểu Ming, rất vui được làm quen.'
    )

async def banudid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = get_news()
    for item in data:
        await update.message.reply_html(item["title"])

# Hàm kiểm tra quyền admin
async def is_admin(update: Update, user_id: int) -> bool:
    chat_id = update.effective_chat.id
    member = await update.effective_chat.get_member(user_id)
    return member.status in ['administrator', 'creator']

# Hàm thực thi lệnh mute
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            await update.message.reply_text(f'Đã tắt tiếng thành viên @{username}.')
        except BadRequest as e:
            await update.message.reply_text(f'Không thể tắt tiếng thành viên: {e.message}')
    else:
        await update.message.reply_text('Vui lòng trả lời tin nhắn của thành viên bạn muốn tắt tiếng.')

# Hàm thực thi lệnh unmute
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True)
            )
            await update.message.reply_text(f'Đã bật tiếng thành viên @{username}.')
        except BadRequest as e:
            await update.message.reply_text(f'Không thể bật tiếng thành viên: {e.message}')
    else:
        await update.message.reply_text('Vui lòng trả lời tin nhắn của thành viên bạn muốn bật tiếng.')

# Hàm thực thi lệnh ban
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

def main() -> None:

    application = ApplicationBuilder().token("7416926704:AAFa4a34XuPaFijKTRNCapb75yyaRoUnf3c").build()

    # Đăng ký các lệnh với Application
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mute", mute))
    application.add_handler(CommandHandler("unmute", unmute))
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(CommandHandler("banudid", banudid))

    # Đặt các lệnh cho bot
    application.bot.set_my_commands([
        BotCommand("start", "Bắt đầu sử dụng bot."),
        BotCommand("mute", "Tắt tiếng thành viên."),
        BotCommand("unmute", "Bật tiếng thành viên."),
        BotCommand("ban", "Cấm thành viên."),
        BotCommand("unban", "Bỏ cấm thành viên.")
    ])

    application.run_polling()

if __name__ == '__main__':
    main()

def main():
    logger.info('Chương trình bắt đầu')
    try:
        # Ví dụ về các hành động trong chương trình
        x = 10
        y = 0
        logger.debug(f'Thực hiện phép chia: {x} / {y}')
        result = x / y
    except ZeroDivisionError as e:
        logger.error(f'Xảy ra lỗi: {e}')
    else:
        logger.info(f'Kết quả: {result}')
    finally:
        logger.info('Chương trình kết thúc')

if __name__ == '__main__':
    main()
