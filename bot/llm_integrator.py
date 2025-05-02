import logging
import os

import google.generativeai as genai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

# --- Configuração do Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = None
gemini_configured = False
response = None


def configure_gemini():
    """Configura a API e o modelo do Gemini."""
    global model, gemini_configured
    if gemini_configured:
        return True

    if not GEMINI_API_KEY:
        logger.warning("A API key do GEMINI não está definida")
        return False
    else:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            logger.info("API Key do Gemini configurada com sucesso.")
            model = genai.GenerativeModel('gemini-2.0-flash-exp')  # gemini-1.5-flash-latest
            logger.info(f"Modelo Gemini '{model.model_name}' inicializado.")
            gemini_configured = True
            return True
        except Exception as e:
            logger.error(f"Falha ao configurar a API do Gemini ou inicializar o modelo: {e}")
            model = None
            gemini_configured = False
            return False


def generate_llm_response(user_question: str, context_info: str = None):
    """
    Gera uma resposta usando o Gemini, opcionalmente usando informações de contexto (grounding).

    Args:
        user_question: A pergunta original do usuário;
        context_info: string contendo informação atual relevante (opcional).

    Returns:
        A resposta de texto gerada pela LLM ou None em caso de erro.
    """
    global response
    if not gemini_configured or model is None:
        logger.error("Tentativa de gerar resposta LLM sem configuração prévia.")
        return None

    try:
        system_prompt = (
            "Você é um assistente chatbot especialista na equipe brasileira de e-sports FURIA. "
            "Responda a seguinte pergunta sobre a equipe (jogadores atuais, staff, resultados recentes, história, etc.) "
            "de forma informativa e engajada.\n"
            "**Instrução Importante:** "
        )

        if context_info:
            system_prompt += (
                "Use PRIMARIAMENTE a 'Informação Atual Relevante' fornecida abaixo para formular sua resposta. "
                "Se a informação necessária não estiver no contexto, use seu conhecimento geral, mas AVISE que a informação pode não ser a mais recente.\n\n"
                "## Informação Atual Relevante:\n"
                f"{context_info}\n\n"
                "## Pergunta do Fã:\n"
                f"{user_question}\n\n"
                "## Sua Resposta:"
            )
        else:
            system_prompt += (
                "Responda à pergunta do fã usando seu conhecimento geral. AVISE que a informação pode não ser a mais recente.\n\n"
                "## Pergunta do Fã:\n"
                f"{user_question}\n\n"
                "## Sua Resposta:"
            )

        full_prompt = system_prompt

        assert isinstance(model, genai.GenerativeModel)
        response = model.generate_content(full_prompt)

        if not response.candidates:
            logger.warning(
                f"Resposta bloqueada para a pergunta '{user_question}'. Feedback: {response.prompt_feedback}")
            return "Desculpe, não posso responder a essa pergunta devido às políticas de segurança."

        llm_response_text = response.text
        logger.info(
            f"Resposta do Gemini para '{user_question}' (com contexto? {'Sim' if context_info else 'Não'}): {llm_response_text[:100]}...")
        return llm_response_text

    except Exception as e:
        logger.error(f"Erro ao chamar a API Gemini para a pergunta '{user_question}': {e}")
        try:
            logger.error(f"Gemini prompt feedback: {response.prompt_feedback}")
        except (Exception,):
            pass
        return None


configure_gemini()
