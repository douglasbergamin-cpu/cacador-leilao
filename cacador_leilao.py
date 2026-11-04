from datetime import datetime
import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests

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


def executar_cacador_real():
  horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  print(
      f"[{horario_atual}] Iniciando caçador com navegador real (Playwright)..."
  )

  # Cidades e termos que você quer monitorar
  cidades_alvo = ["itatiba", "jundiaí"]

  # URLs alvo para varredura real
  urls_para_visitar = [
      "https://www.zukerman.com.br/imoveis/sp/itatiba",
      "https://www.zukerman.com.br/veiculos",
  ]

  encontrados = 0

  with sync_playwright() as p:
    # Abre um navegador invisível (Chromium)
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for url in urls_para_visitar:
      print(f"Acessando via navegador real: {url}")
      try:
        # Acessa a página e espera o conteúdo JS carregar por completo
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  # Espera 5 segundos para o JS renderizar

        html_conteudo = page.content()
        soup = BeautifulSoup(html_conteudo, "html.parser")

        # Procura por blocos de lotes/cards reais no HTML renderizado
        # Vamos varrer todos os links da página renderizada
        for link in soup.find_all("a", href=True):
          href = link["href"]
          texto = link.get_text(strip=True)

          # Verifica se o texto do lote menciona alguma das suas cidades alvo ou termos de interesse
          texto_minusculo = texto.lower()
          if any(cidade in texto_minusculo for cidade in cidades_alvo):
            if (
                len(texto) > 20
            ):  # Garante que é um título de lote real e não um botão do site
              link_completo = (
                  href
                  if href.startswith("http")
                  else f"https://www.zukerman.com.br{href}"
              )

              mensagem = (
                  f"🎯 *OPORTUNIDADE REAL ENCONTRADA!* 🏛️\n\n"
                  f"📌 *Lote/Item:* {texto}\n\n"
                  f"🔗 *[VER LOTE E FOTOS NO SITE]({link_completo})*\n\n"
                  f"⚡ _Capturado pelo navegador automatizado_"
              )
              enviar_alerta_telegram(mensagem)
              encontrados += 1
              print(f"Enviado para o Telegram: {texto[:40]}...")

              # Limita para não disparar dezenas de mensagens repetidas na mesma rodada
              if encontrados >= 5:
                break

      except Exception as e:
        print(f"Erro ao processar a URL {url}: {e}")

    browser.close()

  if encontrados == 0:
    print("Nenhum lote específico com o nome da cidade no texto nesta rodada.")
    enviar_alerta_telegram(
        f"🔍 *Status do Caçador - {horario_atual}*\n\nVarredura com navegador real"
        f" concluída para Itatiba/Jundiaí. Sem lotes nominais novos na Zuk no"
        f" momento, mas o robô de alta precisão está ativo!"
    )


if __name__ == "__main__":
  executar_cacador_real()
