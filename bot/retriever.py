import json
import logging
import os

import requests
from dotenv import load_dotenv

from bot.consts import logger

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")


async def get_current_furia_context(query: str, max_chars: int = 2000) -> str | None:
    """
    Busca informações atuais sobre a FURIA usando a API Serper.dev
    e retorna um resumo do contexto encontrado.

    Args:
        query: A pergunta original do usuário (usada para refinar a busca);
        max_chars: limite aproximado de caracteres para o contexto retornado.

    Returns:
        Uma string com o contexto encontrado ou None se a busca falhar ou não retornar nada útil.
    """
    if not SERPER_API_KEY:
        logger.warning("SERPER_API_KEY não definida. Não é possível buscar contexto atual.")
        return None

    search_query = f"FURIA e-sports {query}"
    logger.info(f"Executando busca na web com Serper: '{search_query}'")

    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = json.dumps({"q": search_query})
    search_url = "https://google.serper.dev/search"

    try:
        response = requests.post(search_url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        results = response.json()

        context_parts = []
        if 'organic' in results:
            for result in results['organic'][:3]:
                title = result.get('title', '')
                link = result.get('link', '')
                snippet = result.get('snippet', '')
                if snippet:
                    context_parts.append(f"- {title}: {snippet} (Fonte: {link})")

        if not context_parts:
            logger.info("Nenhum resultado relevante encontrado na busca Serper.")
            return None

        full_context = "\n".join(context_parts)

        return full_context[:max_chars]

    except requests.exceptions.Timeout:
        logger.error("Timeout ao buscar contexto na API Serper.")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição para a API Serper: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar resposta JSON da Serper: {e}")
        return None
    except Exception as e:
        logger.exception(f"Erro inesperado ao buscar contexto na Serper: {e}")
        return None


if __name__ == '__main__':
    import asyncio

    logging.basicConfig(level=logging.INFO)


    async def run_test():
        question = "Quem é o CTO da FURIA?"
        # question = "Qual foi o ultimo jogo da furia cs?"
        print(f"Buscando contexto para: {question}")
        context = await get_current_furia_context(question)
        if context:
            print("\nContexto Encontrado:\n", context)
        else:
            print("\nNenhum contexto encontrado ou erro na busca.")


    asyncio.run(run_test())
