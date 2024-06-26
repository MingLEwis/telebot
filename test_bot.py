import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, Message, User
from telegram.ext import CallbackContext
from bot import start  # Đảm bảo import đúng hàm start từ tệp bot.py của bạn

@pytest.mark.asyncio
async def test_start():
    # Tạo mock user
    user = User(id=123, first_name='Test', is_bot=False, username='testuser')
    
    # Tạo mock message
    message = Message(message_id=1, date=None, chat=None, from_user=user, text="/start")
    message.reply_text = AsyncMock()
    
    # Tạo mock update với message
    update = Update(update_id=123, message=message)
    
    # Tạo mock context
    context = CallbackContext(dispatcher=None)

    # Gọi hàm start
    await start(update, context)

    # Kiểm tra rằng hàm reply_text đã được gọi với đúng tham số
    message.reply_text.assert_called_once_with('Hi @testuser, tôi là bot Tiểu Ming rất vui được làm quen!')
