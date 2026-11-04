from datetime import datetime
import requests
from bs4 import BeautifulSoup

# ======================================================
# CONFIGURAÇÕES DO TELEGRAM
# ======================================================
TELEGRAM_TOKEN = "9245271479:AAFyUOHNCCMhZDZceyHYYv4AsbRv1iwZa4E"
TELEGRAM_CHAT_ID = "302880433"


def enviar_alerta_telegram(mensagem):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {
      "chat_id": TELEGRAM_CHAT_ID,
      "text": mensagem,
      "parse_mode": "Markdown",
      "disable_web_page_preview": False,
  }
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f"Erro ao enviar no Telegram: {e}")


def executar_agregador():
  horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  print(f"[{horario_atual}] Iniciando varredura multicitadine / multicategoria...")

  # Suas cidades e categorias alvo
  cidades = ["Itatiba", "Jundiaí"]
  encontrou_algo = False

  # Lista de buscas estruturadas nos portais reais
  # Aqui direcionamos para as URLs oficiais de filtro por cidade/categoria
  buscas = []

  for cidade in cidades:
    cidade_url = cidade.lower()
    # Adiciona buscas de Imóveis
    buscas.append({
        "portal": "Zukerman (Imóveis)",
        "categoria": "Imóvel",
        "cidade": cidade,
        "url": f"https://www.zukerman.com.br/imoveis/sp/{cidade_url}",
    })
    # Adiciona buscas de Veículos (geral SP / filtrando a região)
    buscas.append({
        "portal": "Zukerman (Veículos)",
        "categoria": "Veículo",
        "cidade": cidade,
        "url": "https://www.zukerman.com.br/veiculos",
    })

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/122.0.0.0 Safari/537.36"
      ),
      "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
  }

  for alvo in buscas:
    print(f"Verificando {alvo['portal']} para {alvo['cidade']}...")
    try:
      resposta = requests.get(alvo["url"], headers=headers, timeout=15)

      if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.text, "html.parser")

        # Procura por elementos que indiquem lotes ou títulos na página
        # Como o site carrega via JS, vamos validar se a página respondeu e mandar o link de acesso direto refinado
        mensagem = (
            f"🚗/🏠 *OPORTUNIDADE MONITORADA!*\n\n"
            f"🏙️ *Cidade Alvo:* {alvo['cidade']}\n"
            f"📦 *Categoria:* {alvo['categoria']}\n"
            f"🏛️ *Portal:* {alvo['portal']}\n\n"
            f"🔗 *[ABRIR BUSCA DIRETA NO SITE]({alvo['url']})*\n\n"
            f"⚡ _Robô atualizado em {horario_atual}_"
        )
        enviar_alerta_telegram(mensagem)
        encontrou_algo = True

    except Exception as e:
        print(f"Erro ao consultar {alvo['portal']}: {e}")

  if not encontrou_algo:
    enviar_alerta_telegram(
        f"⚠️ O agregador rodou às {horario_atual}, mas houve instabilidade nas"
        " conexões."
    )


if __name__ == "__main__":
  executar_agregador()
