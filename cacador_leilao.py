from datetime import datetime
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


def executar_varredura():
    horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{horario_atual}] Iniciando busca de leilões...")

    cidades = ["itatiba", "jundiai"]
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
    }

    encontrados = 0

    for cidade in cidades:
        url_busca = f"https://www.zukerman.com.br/api/imoveis?cidade={cidade}"
        try:
            resposta = requests.get(url_busca, headers=headers, timeout=15)
            if resposta.status_code == 200:
                dados = resposta.json()
                lotes = dados.get("lotes", []) if isinstance(dados, dict) else []

                for lote in lotes:
                    titulo = lote.get("titulo", f"Lote em {cidade.title()}")
                    link = lote.get("url", f"https://www.zukerman.com.br/imoveis/sp/{cidade}")

                    mensagem = (
                        f"🎯 *OPORTUNIDADE ENCONTRADA!* 🏛️\n\n"
                        f"📍 *Cidade:* {cidade.title()}\n"
                        f"📌 *Item:* {titulo}\n\n"
                        f"🔗 *[ACESSAR LOTE AQUI]({link})*\n\n"
                        f"⚡ _Capturado em {horario_atual}_"
                    )
                    enviar_alerta_telegram(mensagem)
                    encontrados += 1
        except Exception as e:
            print(f"Erro na requisição para {cidade}: {e}")

    if encontrados == 0:
        enviar_alerta_telegram(
            f"🔍 *Status da Varredura - {horario_atual}*\n\n"
            f"Robô executado com sucesso. Nenhum novo lote listado para Itatiba/Jundiaí no momento."
        )


if __name__ == "__main__":
    executar_varredura()
