import pytest
from unittest.mock import AsyncMock, patch
from telegram import Update, Message, User, Chat
from telegram.ext import CallbackContext
from bot import start  # Đảm bảo import đúng hàm start từ tệp bot.py của bạn

@pytest.mark.asyncio
async def test_start():
    # Tạo mock user
    user = User(id=123, first_name='Test', is_bot=False, username='testuser')
    
    # Tạo mock chat
    chat = Chat(id=1, type='private')

    # Tạo mock message
    message = Message(message_id=1, date=None, chat=chat, from_user=user, text="/start")

    # Tạo mock update với message
    update = Update(update_id=123, message=message)

    # Tạo mock context
    context = CallbackContext()

    # Mock phương thức reply_text của message
    with patch.object(Message, 'reply_text', new=AsyncMock()) as mock_reply:
        # Gọi hàm start
        await start(update, context)

        # Kiểm tra rằng hàm reply_text đã được gọi với đúng tham số
        mock_reply.assert_called_once_with('Hi @testuser, tôi là bot Tiểu Ming rất vui được làm quen!')
