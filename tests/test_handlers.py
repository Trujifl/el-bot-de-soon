import pytest
from telegram import Update
from unittest.mock import AsyncMock, MagicMock
from src.handlers.base import start, help_command


@pytest.mark.asyncio
async def test_start_handler():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.effective_user.first_name = "TestUser"
    context = MagicMock()
    
    await start(update, context)
    
    assert update.message.reply_text.called
    assert "TestUser" in update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_help_handler():
    update = MagicMock()
    update.message = MagicMock()
    context = MagicMock()
    
    await help_command(update, context)
    
    assert update.message.reply_text.called
    assert "comandos" in update.message.reply_text.call_args[0][0].lower()