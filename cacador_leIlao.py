import os
from datetime import datetime
import requests

# ======================================================
# CONFIGURAÇÕES DO TELEGRAM
# ======================================================
TELEGRAM_TOKEN = "9245271479:AAFyUOHNCCMhZDZceyHYYv4AsbRv1iwZa4E"
TELEGRAM_CHAT_ID = "302880433"


def enviar_alerta_telegram(mensagem):
  """Envia o alerta oficial direto para o seu Telegram."""
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {
      "chat_id": TELEGRAM_CHAT_ID,
      "text": mensagem,
      "parse_mode": "Markdown",
      "disable_web_page_preview": False,
  }
  try:
    requests.post(url, json=payload, timeout=10)
    print("📲 Alerta com link real enviado com sucesso!")
  except Exception as e:
    print(f"❌ Erro ao enviar no Telegram: {e}")


def executar_varredura_leiloes():
  horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  print(f"==================================================")
  print(f"🏛️ BUSCA DIRETA DE LEILÕES REAIS - {horario_atual}")
  print(f"==================================================")

  # Links oficiais diretos com o filtro da nossa região (Itatiba / Jundiaí / SP)
  portais_reais = [
      {
          "nome": "Zuk Leilões (Imóveis - Região Itatiba/Jundiaí)",
          "url": "https://www.zukerman.com.br/imoveis/sp/itatiba",
      },
      {
          "nome": "Superbid (Bens e Veículos - Interior SP)",
          "url": "https://www.superbid.net/busca?q=Itatiba&state%5B0%5D=SP",
      },
      {
          "nome": "Portal e-Leilões (Tribunal de Justiça de SP)",
          "url": "https://www.e-leiloes.com.br/por-comarca/itatiba-sp",
      },
  ]

  for portal in portais_reais:
    mensagem = (
        f"🎯 *ACESSO DIRETO AO LEILÃO REAL* 🏛️\n\n"
        f"🏢 *Portal Oficial:* `{portal['nome']}`\n"
        f"📍 *Foco:* Itatiba / Jundiaí e Região\n\n"
        f"🔍 *[CLIQUE AQUI PARA ABRIR A PÁGINA COM OS LOTES E FOTOS]"
        f"({portal['url']})*\n\n"
        f"⚡ _Acesse agora para ver os editais e lotes ativos!_"
    )
    enviar_alerta_telegram(mensagem)


if __name__ == "__main__":
  executar_varredura_leiloes()
