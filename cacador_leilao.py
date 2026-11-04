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


def executar_varredura_real():
  horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  print(f"[{horario_atual}] Iniciando varredura real...")

  # URL real de busca para Itatiba
  url_alvo = "https://www.zukerman.com.br/imoveis/sp/itatiba"

  # Headers essenciais para o site reconhecer como um navegador real
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/122.0.0.0 Safari/537.36"
      ),
      "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
  }

  try:
    resposta = requests.get(url_alvo, headers=headers, timeout=15)

    if resposta.status_code != 200:
      print(f"❌ Erro ao acessar o site. Status code: {resposta.status_code}")
      enviar_alerta_telegram(
          f"⚠️ *Aviso do Robô*\n\nO site da Zuk retornou status"
          f" `{resposta.status_code}` ao tentar buscar Itatiba."
      )
      return

    # Parseia o HTML real da página
    soup = BeautifulSoup(resposta.text, "html.parser")
    encontrados = 0

    # Varre os links procurando por lotes reais da região
    for link in soup.find_all("a", href=True):
      href = link["href"]
      texto = link.get_text(strip=True)

      if "/imovel/" in href or "itatiba" in href.lower():
        if len(texto) > 15:
          link_completo = (
              href if href.startswith("http") else f"https://www.zukerman.com.br{href}"
          )

          mensagem = (
              f"🎯 *LOTE REAL ENCONTRADO EM ITATIBA!* 🏛️\n\n"
              f"📌 *Título:* {texto}\n\n"
              f"🔗 *[CLIQUE AQUI PARA VER O LOTE E FOTOS]({link_completo})*\n\n"
              f"⚡ _Capturado automaticamente pelo robô._"
          )
          enviar_alerta_telegram(mensagem)
          encontrados += 1
          print(f"Lote enviado: {texto[:30]}...")

          if encontrados >= 3:
            break

    if encontrados == 0:
      print(
          "⚠️ Nenhum lote isolado diretamente, enviando notificação de varredura"
          " concluída."
      )
      enviar_alerta_telegram(
          f"🔍 *Varredura Real Concluída - Itatiba*\n\nVarreu a página da Zuk"
          f" com sucesso às {horario_atual}, mas sem novos lotes filtrados no"
          f" momento.\n\n[Abrir Página da Zuk]({url_alvo})"
      )

  except Exception as e:
    print(f"❌ Erro na execução: {e}")


if __name__ == "__main__":
  executar_varredura_real()
