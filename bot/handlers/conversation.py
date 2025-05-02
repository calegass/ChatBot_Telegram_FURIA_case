from telegram import Update, ReplyKeyboardRemove
from telegram.constants import ChatAction
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from bot.consts import (
    STATE_MAIN_MENU,
    STATE_SHOWING_RESULTS,
    STATE_AWAITING_QUESTION,
    MENU_MARKUP,
    RESULTS_MARKUP,
    BUTTON_ACTIONS,
    TEXT_WELCOME,
    TEXT_MAIN_MENU_FALLBACK,
    TEXT_BACK_TO_MAIN,
    TEXT_EXIT,
    TEXT_FALLBACK_GENERAL,
    TEXT_ASK_QUESTION_PROMPT,
    TEXT_CANCEL_ACTION,
    TEXT_SEARCHING_LAST_RESULTS,
    TEXT_SEARCHING_MORE_RESULTS,
    TEXT_NO_MORE_RESULTS,
    TEXT_NO_RESULTS_FOUND,
    TEXT_RESULTS_ERROR,
    TEXT_QUESTION_UNAVAILABLE,
    TEXT_LLM_ERROR,
    TEXT_LLM_DISCLAIMER,
    logger
)
from bot.llm_integrator import generate_llm_response, gemini_configured
from bot.retriever import get_current_furia_context
from bot.scraper import get_furia_latest_results


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia a conversa com o usuário e exibe o menu principal."""
    logger.info(f"Usuário {update.effective_user.id} iniciou a conversa.")
    context.user_data.clear()
    await update.message.reply_text(TEXT_WELCOME, reply_markup=MENU_MARKUP)
    return STATE_MAIN_MENU


async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exibe os últimos resultados da FURIA."""
    user_id = update.effective_user.id
    logger.info(f"Usuário {user_id} pediu resultados.")
    await update.message.reply_text(TEXT_SEARCHING_LAST_RESULTS)

    results = get_furia_latest_results(count=5)

    if results is None:
        await update.message.reply_text(TEXT_RESULTS_ERROR, reply_markup=MENU_MARKUP)
        return STATE_MAIN_MENU
    elif not results:
        await update.message.reply_text(TEXT_NO_RESULTS_FOUND, reply_markup=RESULTS_MARKUP)
    else:
        message_text = "*Últimos Resultados da FURIA:*\n\n"
        for r in results:
            emoji = "❓"
            try:
                if int(r['furia_score']) > int(r['opponent_score']):
                    emoji = "✅"
                elif int(r['furia_score']) < int(r['opponent_score']):
                    emoji = "❌"
            except ValueError:
                pass
            message_text += (
                f"{emoji} *FURIA {r['furia_score']} x {r['opponent_score']} {r['opponent_name']}*\n"
                f"📅 {r['date']}\n"
                f"🏆 _{r['tournament_name']}_\n\n"
            )
        context.user_data['last_results'] = results
        context.user_data['results_offset'] = len(results)
        await update.message.reply_text(message_text, reply_markup=RESULTS_MARKUP, parse_mode='Markdown')

    return STATE_SHOWING_RESULTS


async def show_more_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exibe mais resultados da FURIA."""
    user_id = update.effective_user.id
    logger.info(f"Usuário {user_id} pediu mais resultados.")
    current_offset = context.user_data.get('results_offset', 5)
    results_to_fetch = 5
    await update.message.reply_text(TEXT_SEARCHING_MORE_RESULTS)

    total_to_fetch = current_offset + results_to_fetch
    all_results = get_furia_latest_results(count=total_to_fetch)

    if all_results is None:
        await update.message.reply_text(TEXT_RESULTS_ERROR, reply_markup=RESULTS_MARKUP)
        return STATE_SHOWING_RESULTS
    elif len(all_results) <= current_offset:
        await update.message.reply_text(TEXT_NO_MORE_RESULTS, reply_markup=RESULTS_MARKUP)
    else:
        new_results = all_results[current_offset:total_to_fetch]
        message_text = "*Resultados Adicionais:*\n\n"
        for r in new_results:
            emoji = "❓"
            try:
                if int(r['furia_score']) > int(r['opponent_score']):
                    emoji = "✅"
                elif int(r['furia_score']) < int(r['opponent_score']):
                    emoji = "❌"
            except ValueError:
                pass
            message_text += (
                f"{emoji} *FURIA {r['furia_score']} x {r['opponent_score']} {r['opponent_name']}*\n"
                f"📅 {r['date']}\n"
                f"🏆 _{r['tournament_name']}_\n\n"
            )
        context.user_data['results_offset'] = len(all_results)
        await update.message.reply_text(message_text, reply_markup=RESULTS_MARKUP, parse_mode='Markdown')

    return STATE_SHOWING_RESULTS


async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Retorna o usuário ao menu principal."""
    user_id = update.effective_user.id
    logger.info(f"Usuário {user_id} voltou/cancelou para o menu principal.")
    context.user_data.pop('choice', None)
    context.user_data.pop('last_results', None)
    context.user_data.pop('results_offset', None)
    await update.message.reply_text(TEXT_BACK_TO_MAIN, reply_markup=MENU_MARKUP)
    return STATE_MAIN_MENU


async def exit_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Encerra a conversa com o usuário."""
    user_id = update.effective_user.id
    logger.info(f"Usuário {user_id} encerrou a conversa via {update.message.text}.")
    context.user_data.clear()
    await update.message.reply_text(TEXT_EXIT, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def prompt_for_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Solicita ao usuário que faça uma pergunta."""
    logger.info(f"Usuário {update.effective_user.id} selecionou fazer pergunta.")
    await update.message.reply_text(TEXT_ASK_QUESTION_PROMPT, reply_markup=ReplyKeyboardRemove())
    return STATE_AWAITING_QUESTION


async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processa a pergunta do usuário e gera uma resposta usando LLM."""
    user_question = update.message.text
    user_id = update.effective_user.id
    logger.info(f"Usuário {user_id} fez a pergunta: '{user_question}'")

    if not gemini_configured:
        logger.error(f"Tentativa de usar LLM sem configuração pelo usuário {user_id}.")
        await update.message.reply_text(TEXT_QUESTION_UNAVAILABLE, reply_markup=MENU_MARKUP)
        return STATE_MAIN_MENU

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    logger.info(f"Buscando contexto atual para a pergunta: '{user_question}'")
    context_info = await get_current_furia_context(user_question)

    if context_info:
        logger.info(f"Contexto encontrado: {context_info[:100]}...")
    else:
        logger.info("Nenhum contexto adicional encontrado, usando conhecimento geral da LLM.")

    llm_response_text = generate_llm_response(user_question, context_info)

    if llm_response_text:
        await update.message.reply_text(llm_response_text)
        await update.message.reply_text(TEXT_LLM_DISCLAIMER, parse_mode='Markdown')
    else:
        await update.message.reply_text(TEXT_LLM_ERROR)

    return await back_to_main_menu(update, context)


async def cancel_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela a ação atual e retorna ao menu principal."""
    user_id = update.effective_user.id
    logger.info(f"Usuário {user_id} cancelou a ação via /cancel.")
    await update.message.reply_text(TEXT_CANCEL_ACTION)
    return await back_to_main_menu(update, context)


async def main_menu_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Lida com entradas inesperadas no menu principal."""
    logger.warning(f"Input inesperado no menu principal do usuário {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text(TEXT_MAIN_MENU_FALLBACK, reply_markup=MENU_MARKUP)
    return STATE_MAIN_MENU


async def results_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Lida com entradas inesperadas na tela de resultados."""
    logger.warning(f"Input inesperado nos resultados do usuário {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text(TEXT_FALLBACK_GENERAL, reply_markup=RESULTS_MARKUP)
    return STATE_SHOWING_RESULTS


# --- Configuração do ConversationHandler ---
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        STATE_MAIN_MENU: [
            MessageHandler(filters.Regex(BUTTON_ACTIONS["SHOW_RESULTS"][1]), show_results),
            MessageHandler(filters.Regex(BUTTON_ACTIONS["ASK_QUESTION"][1]), prompt_for_question),
            MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_fallback),
        ],
        STATE_SHOWING_RESULTS: [
            MessageHandler(filters.Regex(BUTTON_ACTIONS["SHOW_MORE"][1]), show_more_results),
            MessageHandler(filters.Regex(BUTTON_ACTIONS["BACK_TO_MAIN"][1]), back_to_main_menu),
            MessageHandler(filters.TEXT & ~filters.COMMAND, results_fallback),
        ],
        STATE_AWAITING_QUESTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question),
        ],
    },
    fallbacks=[
        CommandHandler("start", start),
        CommandHandler("cancel", cancel_action),
        CommandHandler("sair", exit_conversation),
    ],
    name="furia_conversation",
    persistent=True,
)
