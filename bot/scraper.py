# bot/scraper.py

import json
import logging
from datetime import datetime, timezone, timedelta

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

DRAFT5_FURIA_RESULTS_URL = "https://draft5.gg/equipe/330-FURIA/resultados"
TEAM_ID_FURIA = 330

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def format_match_result(match_data):
    """Formata os dados de uma única partida em um dicionário mais limpo."""
    try:
        team_a = match_data.get('teamA', {})
        team_b = match_data.get('teamB', {})
        tournament = match_data.get('tournament', {})
        timestamp = match_data.get('matchDate')

        if team_a.get('teamId') == TEAM_ID_FURIA:
            opponent_team = team_b
            furia_score = match_data.get('seriesScoreA')
            opponent_score = match_data.get('seriesScoreB')
        elif team_b.get('teamId') == TEAM_ID_FURIA:
            opponent_team = team_a
            furia_score = match_data.get('seriesScoreB')
            opponent_score = match_data.get('seriesScoreA')
        else:
            opponent_team = team_b
            furia_score = match_data.get('seriesScoreA')
            opponent_score = match_data.get('seriesScoreB')
            logger.warning(
                f"FURIA team ID ({TEAM_ID_FURIA}) not found in match {match_data.get('matchId')}. Using Team A as FURIA.")

        date_str = "Data indisponível"
        if timestamp:
            dt_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            dt_brt = dt_utc.astimezone(timezone(timedelta(hours=-3)))
            date_str = dt_brt.strftime('%d/%m/%Y %H:%M')

        result = {
            'furia_score': furia_score if furia_score is not None else '?',
            'opponent_score': opponent_score if opponent_score is not None else '?',
            'opponent_name': opponent_team.get('teamName', 'Desconhecido'),
            'tournament_name': tournament.get('tournamentName', 'Torneio desconhecido'),
            'date': date_str,
            'match_id': match_data.get('matchId')
        }
        return result

    except Exception as e:
        logger.error(f"Erro ao formatar dados da partida {match_data.get('matchId', 'N/A')}: {e}")
        return None


def fetch_results_data(url=DRAFT5_FURIA_RESULTS_URL):
    """Busca e parseia os dados JSON da página de resultados."""
    logger.info(f"Buscando resultados de: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', {'id': '__NEXT_DATA__'})

        if not script_tag:
            logger.error("Não foi possível encontrar a tag <script id='__NEXT_DATA__'>")
            return None

        json_data = json.loads(script_tag.string)
        return json_data

    except requests.exceptions.Timeout:
        logger.error(f"Timeout ao tentar buscar a URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição para {url}: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar o JSON da tag <script>: {e}")
        return None
    except Exception as e:
        logger.exception(
            f"Erro inesperado ao buscar/parsear dados de {url}: {e}")
        return None


def get_furia_latest_results(count=5):
    """Busca os 'count' últimos resultados da FURIA no Draft5."""
    json_data = fetch_results_data()
    if not json_data:
        return None

    try:
        results_list = json_data['props']['pageProps']['results']
        if not results_list:
            logger.info("Lista de resultados ('results') vazia no JSON.")
            return []

        formatted_results = []
        for match in results_list[:count]:
            formatted = format_match_result(match)
            if formatted:
                formatted_results.append(formatted)

        logger.info(f"Encontrados e formatados {len(formatted_results)} resultados.")
        return formatted_results

    except KeyError as e:
        logger.error(f"Estrutura do JSON inesperada. Chave não encontrada: {e}")
        return None
    except Exception as e:
        logger.exception(f"Erro inesperado ao processar a lista de resultados: {e}")
        return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    latest_results = get_furia_latest_results(count=3)
    if latest_results is None:
        print("Falha ao buscar resultados.")
    elif not latest_results:
        print("Nenhum resultado encontrado.")
    else:
        print(f"Últimos {len(latest_results)} resultados:")
        for r in latest_results:
            print(
                f"- {r['date']}: FURIA {r['furia_score']} x {r['opponent_score']} {r['opponent_name']} ({r['tournament_name']})")
