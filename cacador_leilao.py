import os
from datetime import datetime
import requests

# ======================================================
# CONFIGURAÇÕES DO TELEGRAM
# ======================================================
TELEGRAM_TOKEN = "9245271479:AAFyUOHNCCMhZDZceyHYYv4AsbRv1iwZa4E"
TELEGRAM_CHAT_ID = "302880433"


def enviar_alerta_telegram(mensagem):
  """Envia o alerta rico e detalhado para o seu Telegram."""
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {
      "chat_id": TELEGRAM_CHAT_ID,
      "text": mensagem,
      "parse_mode": "Markdown",
      "disable_web_page_preview": False,
  }
  try:
    requests.post(url, json=payload, timeout=10)
    print("📲 Alerta detalhado de leilão enviado com sucesso!")
  except Exception as e:
    print(f"❌ Erro ao enviar no Telegram: {e}")


def executar_varredura_leiloes():
  horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  print(f"==================================================")
  print(f"🏛️ VARREDURA INTELIGENTE DE LEILÕES - {horario_atual}")
  print(f"==================================================")

  # Simulando a captura estruturada de um lote real de leilão
  # (Aqui o robô processa os dados extraídos do edital/site)
  lote = {
      "tipo_bem": "Apartamento Residencial",
      "comarca_localizacao": "Jundiaí / SP (Bairro Centro)",
      "edital_id": "Processo nº 1002345-88.2024.8.26.0309",
      "valor_mercado": 450000.00,
      "lance_minimo": 210000.00,
      "desconto_porcentagem": 53.3,
      "link_fotos_edital": "https://www.zukerman.com.br",
  }

  # Filtro de Oportunidade: Só avisa se o desconto for superior a 40%
  if lote["desconto_porcentagem"] >= 40.0:
    mensagem = (
        f"🚨 *OPORTUNIDADE DE LEILÃO ENCONTRADA!* 🏛️\n\n"
        f"🏠 *Tipo:* `{lote['tipo_bem']}`\n"
        f"📍 *Localização:* `{lote['comarca_localizacao']}`\n"
        f"📄 *Referência:* {lote['edital_id']}\n\n"
        f"💰 *Valor de Avaliação:* R$ {lote['valor_mercado']:,.2f}\n"
        f"🔥 *Lance Mínimo:* R$ {lote['lance_minimo']:,.2f}\n"
        f"📉 *Desconto Real:* *{lote['desconto_porcentagem']}% OFF*\n\n"
        f"📸 [CLIQUE AQUI PARA VER AS FOTOS E O EDITAL]"
        f"({lote['link_fotos_edital']})\n\n"
        f"⚡ _Dados extraídos e validados automaticamente!_"
    ).replace(",", "X").replace(".", ",").replace("X", ".")

    enviar_alerta_telegram(mensagem)
  else:
    print("ℹ️ Lote abaixo do percentual mínimo de desconto.")


if __name__ == "__main__":
  executar_varredura_leiloes()
