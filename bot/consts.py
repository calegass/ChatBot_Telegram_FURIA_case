import logging
import re

from telegram import ReplyKeyboardMarkup

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

STATE_MAIN_MENU, STATE_SHOWING_RESULTS, STATE_AWAITING_QUESTION = range(3)

# --- Textos e Regex dos Botões ---
# Estrutura: {NOME_AÇÃO: (Texto Visível, Padrão Regex)}
BUTTON_ACTIONS = {
    "SHOW_RESULTS": ("Ver resultados dos jogos", rf"^{re.escape('Ver resultados dos jogos')}$"),
    "ASK_QUESTION": ("Fazer alguma pergunta", rf"^{re.escape('Fazer alguma pergunta')}$"),
    "SHOW_MORE": ("Ver mais jogos", rf"^{re.escape('Ver mais jogos')}$"),
    "BACK_TO_MAIN": ("Voltar ao menu principal", rf"^{re.escape('Voltar ao menu principal')}$"),
    "EXIT": ("/sair", rf"^{re.escape('/sair')}$"),
}

# --- Teclados (Markups) ---
MENU_OPTIONS = [
    [BUTTON_ACTIONS["SHOW_RESULTS"][0]],
    [BUTTON_ACTIONS["ASK_QUESTION"][0]],
    [BUTTON_ACTIONS["EXIT"][0]]
]
MENU_MARKUP = ReplyKeyboardMarkup(MENU_OPTIONS, one_time_keyboard=True, resize_keyboard=True)

RESULTS_OPTIONS = [
    [BUTTON_ACTIONS["SHOW_MORE"][0]],
    [BUTTON_ACTIONS["BACK_TO_MAIN"][0]]
]
RESULTS_MARKUP = ReplyKeyboardMarkup(RESULTS_OPTIONS, one_time_keyboard=True, resize_keyboard=True)

# --- Textos no geral ---
TEXT_WELCOME = "🔥 Bem-vindo ao bot da FURIA!\n\n_Esse bot foi desenvolvido por Matheus Calegari como parte do Desafio Técnico para Assistente de Engenharia de Software na FURIA_\n\nEscolha uma das opções abaixo para continuar:"
TEXT_MAIN_MENU_FALLBACK = "Não entendi. Use o menu para escolher uma opção."
TEXT_BACK_TO_MAIN = "Voltando ao menu principal..."
TEXT_EXIT = "👋 Até a próxima! FURIA! (Use /start para conversar novamente)"
TEXT_ERROR = "Ocorreu um erro inesperado. Por favor, tente iniciar novamente com /start."
TEXT_FALLBACK_GENERAL = "Desculpe, não entendi esse comando nesse contexto. Use os botões ou os comandos disponíveis."
TEXT_ASK_QUESTION_PROMPT = "Ok, pode fazer sua pergunta sobre a FURIA (ou digite /cancel para voltar):"
TEXT_CANCEL_ACTION = "Ação cancelada. Voltando ao menu."
TEXT_SEARCHING_LAST_RESULTS = "🔍 Buscando os últimos resultados da FURIA..."
TEXT_SEARCHING_MORE_RESULTS = "🔍 Buscando mais resultados..."
TEXT_NO_MORE_RESULTS = "Não encontrei mais resultados."
TEXT_NO_RESULTS_FOUND = "Não encontrei resultados recentes."
TEXT_RESULTS_ERROR = "Desculpe, não consegui buscar os resultados agora. Tente novamente mais tarde."
TEXT_QUESTION_UNAVAILABLE = "Desculpe, a função de perguntas está temporariamente indisponível."
TEXT_LLM_ERROR = "Desculpe, não consegui gerar uma resposta neste momento. Tente novamente mais tarde."
TEXT_LLM_DISCLAIMER = "_Resposta gerada por IA. Informações atuais dependem da busca de contexto._"
TEXT_AWAITING_QUESTION_FALLBACK = "Por favor, digite sua pergunta ou use /cancel para voltar ao menu."
