# Telegram Bot para a FURIA

Este projeto foi desenvolvido como parte de um teste técnico, para criar uma experiência conversacional
útil e engajadora para a torcida, por Matheus Calegari.

---

## Funcionalidades Principais

* **Resultados de Jogos:** Veja os últimos resultados das partidas de CS da FURIA, obtidos via web scraping
  do [Draft5.gg](https://draft5.gg/).
    * Inclui placares, oponente, data e nome do torneio.
    * Opção "Ver mais jogos" para carregar resultados anteriores (paginação simulada).
* **Perguntas e Respostas (IA):** Faça perguntas em linguagem natural sobre a FURIA (Ex: "Quem são os jogadores
  atuais?", "Qual foi o último resultado contra a G2?", "Quem é o CTO da Furia?").
    * Utiliza a API do **Google Gemini** (`gemini-2.0-flash-exp`) para gerar respostas.
    * **Grounding:** Antes de responder, o bot busca informações atualizadas na
      web usando a **Serper API** para fornecer contexto recente ao Gemini, garantindo respostas mais precisas sobre
      eventos e informações atuais.
* **Interface Conversacional:** Gerenciamento de estado da conversa com menus interativos usando
  `python-telegram-bot`.
* **Dockerizado:** Pronto para ser executado facilmente usando Docker e Docker Compose, necessitando apenas de
  configurar chaves em .env.

---

## Tecnologias Utilizadas

* **Linguagem:** Python 3.13
* **Biblioteca do Bot:** `python-telegram-bot` (com persistência `PicklePersistence`)
* **Web Scraping:** `requests`, `beautifulsoup4` (para resultados do Draft5)
* **Inteligência Artificial (LLM):** Google Gemini API (`google-generativeai`)
* **Busca Web (RAG):** Serper API (`requests`)
* **Variáveis de Ambiente:** `python-dotenv`
* **Containerização:** Docker, Docker Compose
* **Gerenciador de pacotes:** UV

---

## Como Usar o Bot no Telegram

* **Inicie a Conversa:** Encontre seu bot no Telegram e envie o comando `/start`.
* **Menu Principal:** Você verá as opções:
    * **Ver resultados dos jogos:** Mostra os últimos resultados e oferece opções para ver mais ou voltar.
    * **Fazer alguma pergunta:** Permite que você digite uma pergunta sobre a FURIA. O bot buscará informações atuais e
      usará a IA Gemini para responder.

* Comandos Adicionais:
    * **`/cancel`:** Pode ser usado a qualquer momento (especialmente útil se você selecionou "Fazer pergunta" e quer
      desistir) para retornar ao menu principal.
    * **`/sair`:** Uma alternativa para encerrar a conversa.
    * **`/start`:** Pode ser usado a qualquer momento para reiniciar a conversa do zero.

---

## Configuração e Execução

Existem duas maneiras principais de executar o bot: localmente ou via Docker (recomendado).

**Pré-requisitos:**

* Git
* Python 3.13 ou superior (se for rodar localmente) (idealmente 3.13.3 que foi o que usei e não testei em versões
  anteriores/superiores)
* Pip (gerenciador de pacotes Python)
* Docker e Docker Compose (se for usar Docker)
* Contas e Chaves de API:
    * **Telegram Bot Token:** Criação de um bot no Telegram falando com o [@BotFather](https://t.me/BotFather) e
      obtenção do token.
    * **Google Gemini API Key:** Disponível em [Google AI Studio](https://aistudio.google.com/).
    * **Serper API Key:** Disponível em [serper.dev](https://serper.dev/) (necessária para a busca web no RAG).

**1. Clonar o Repositório:**

```bash
git clone https://github.com/calegass/ChatBot_Telegram_FURIA_case.git
cd ChatBot_Telegram_FURIA_case
```

**2. Configurar Variáveis de Ambiente:**

Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis:

```
TELEGRAM_TOKEN
GOOGLE_API_KEY
SERPER_API_KEY
```

**3. Rodar o Docker Compose:**

```bash
docker-compose up --build -d
```

Para acompanhar os logs do bot, você pode usar: `docker-compose logs -f furia-bot`
