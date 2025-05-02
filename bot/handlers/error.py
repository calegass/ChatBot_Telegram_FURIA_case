from telegram import Update
from telegram.ext import ContextTypes

from bot.consts import logger, TEXT_ERROR


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Loga os erros causados por Updates e envia mensagem genérica."""
    logger.error("Exceção não tratada:", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(TEXT_ERROR)
        except Exception as e:
            logger.error(f"Falha ao enviar mensagem de erro para o usuário: {e}")
