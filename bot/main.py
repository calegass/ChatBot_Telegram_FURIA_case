import os

import httpx
from dotenv import load_dotenv
from telegram.constants import ParseMode
from telegram.ext import Application, PicklePersistence, Defaults

from bot.consts import logger
from bot.handlers.conversation import conv_handler
from bot.handlers.error import error_handler

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY or not SERPER_API_KEY:
    logger.critical("Variáveis de ambiente vazias")
    exit(1)


def main() -> None:
    """Essa função inicia o bot e configura os handlers de
    conversação e de erro, além de lidar com exceções."""
    logger.info("Iniciando o bot...")

    persistence = PicklePersistence(filepath="../furia_bot_data")

    defaults = Defaults(parse_mode=ParseMode.MARKDOWN)

    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .persistence(persistence)
        .defaults(defaults)
        .build()
    )

    application.add_handler(conv_handler)

    application.add_error_handler(error_handler)

    try:
        logger.info("Bot iniciado e escutando por updates...")
        application.run_polling()

    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot sendo parado manualmente (Ctrl+C ou SystemExit)...")
    except httpx.ConnectError as e:
        logger.exception("Erro de conexão com o servidor: %s", e)
        main()
    except Exception as e:
        logger.exception(f"Ocorreu uma exceção fatal no loop principal: {e}")
    finally:
        logger.info("Bot finalizado.")


main()
