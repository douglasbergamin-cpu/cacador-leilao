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


def varrer_portal(nome_portal, url_busca, termo_chave):
  print(f"Varredura em andamento no {nome_portal} para: {termo_chave}")

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/122.0.0.0 Safari/537.36"
      ),
      "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
  }

  encontrados = []
  try:
    resposta = requests.get(url_busca, headers=headers, timeout=15)
    if resposta.status_code != 200:
      print(f"❌ {nome_portal} retornou status {resposta.status_code}")
      return encontrados

    soup = BeautifulSoup(resposta.text, "html.parser")

    # Varre os links da página procurando menção à cidade ou termo alvo
    for link in soup.find_all("a", href=True):
      href = link["href"]
      texto = link.get_text(strip=True)

      # Filtra se o texto ou link contêm a cidade desejada (ex: itatiba)
      if termo_chave.lower() in texto.lower() or termo_chave.lower() in href.lower():
        if len(texto) > 10:
          link_completo = (
              href
              if href.startswith("http")
              else f"https://www.{nome_portal.lower()}.com.br{href}"
          )
          if link_completo not in encontrados:
            encontrados.append((texto, link_completo))

  except Exception as e:
    print(f"Erro ao varrer {nome_portal}: {e}")

  return encontrados


def executar_varredura_geral():
  horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  cidade_alvo = "Itatiba"

  print(f"[{horario_atual}] Iniciando varredura multileiloeiro...")

  # Lista de portais e URLs base de busca para testar
  portais = [
      {
          "nome": "Zukerman",
          "url": f"https://www.zukerman.com.br/imoveis/sp/{cidade_alvo.lower()}",
      },
      # Adicionamos uma busca geral no estado para filtrar o que cair na cidade
      {
          "nome": "Zukerman Geral SP",
          "url": "https://www.zukerman.com.br/imoveis/sp",
      },
  ]

  total_encontrados = 0

  for portal in portais:
    resultados = varrer_portal(
        portal["nome"], portal["url"], cidade_alvo
    )

    for titulo, link in resultados[:3]:  # Limita para não floodar
      mensagem = (
          f"🎯 *OPORTUNIDADE EM {cidade_alvo.upper()}!* 🏛️\n\n"
          f"🏢 *Portal:* {portal['nome']}\n"
          f"📌 *Item:* {titulo}\n\n"
          f"🔗 *[ACESSAR O LOTE NO SITE]({link})*\n\n"
          f"⚡ _Capturado pelo seu Agregador Automático_"
      )
      enviar_alerta_telegram(mensagem)
      total_encontrados += 1

  if total_encontrados == 0:
    print("Nenhum lote novo isolado nesta rodada.")
    # Manda um resumo de que rodou e está monitorando
    enviar_alerta_telegram(
        f"🔍 *Status do Agregador - {horario_atual}*\n\nVarredura multileiloeiro"
        f" concluída para *{cidade_alvo}*. Nenhum lote novo com o filtro exato"
        f" no momento, mas o robô segue de olho!"
    )


if __name__ == "__main__":
  executar_varredura_geral()
