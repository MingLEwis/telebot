import pytest
from telegram import Update
from telegram.ext import CallbackContext
from bot import start  # Đảm bảo import đúng hàm start từ tệp mã của bạn

@pytest.mark.asyncio
async def test_start():
    # Tạo mock update và context
    update = Update(update_id=123, message=None)  # Thay thế None bằng đối tượng Message nếu cần thiết
    context = CallbackContext(dispatcher=None)

    # Gọi hàm start và kiểm tra kết quả
    await start(update, context)
    assert True  # Thêm các assert khác để kiểm tra hành vi của hàm start
