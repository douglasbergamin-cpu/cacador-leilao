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
    print(f"[{horario_atual}] Iniciando varredura real de leilões...")

    # Cidades e termos que você deseja monitorar
    cidades_alvo = ["itatiba", "jundiaí", "jundiai"]

    # Páginas alvo de busca na Zukerman (Imóveis e Veículos)
    urls_alvo = [
        "https://www.zukerman.com.br/imoveis/sp/itatiba",
        "https://www.zukerman.com.br/imoveis/sp/jundiai",
        "https://www.zukerman.com.br/veiculos"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    encontrados = 0

    for url_alvo in urls_alvo:
        try:
            print(f"Varrendo URL: {url_alvo}")
            resposta = requests.get(url_alvo, headers=headers, timeout=15)

            if resposta.status_code != 200:
                print(f"⚠️ Alerta: URL retornou status {resposta.status_code}")
                continue

            soup = BeautifulSoup(resposta.text, "html.parser")

            # Procura por todos os links na página que possam conter lotes
            for link in soup.find_all("a", href=True):
                href = link["href"]
                texto = link.get_text(strip=True)
                texto_lower = texto.lower()

                # Verifica se o link menciona alguma das cidades alvo ou se é uma página de lote válida
                if any(cidade in texto_lower or cidade in href.lower() for cidade in cidades_alvo):
                    if len(texto) > 15:  # Garante que é um título descritivo real
                        link_completo = href if href.startswith("http") else f"https://www.zukerman.com.br{href}"

                        mensagem = (
                            f"🎯 *OPORTUNIDADE ENCONTRADA!* 🏛️\n\n"
                            f"📌 *Item:* {texto}\n\n"
                            f"🔗 *[ACESSAR LOTE E FOTOS]({link_completo})*\n\n"
                            f"⚡ _Capturado pelo seu Agregador Automatizado_"
                        )
                        enviar_alerta_telegram(mensagem)
                        encontrados += 1
                        print(f"Lote enviado: {texto[:40]}...")

                        if encontrados >= 6:  # Limita para não floodar
                            break

        except Exception as e:
            print(f"Erro ao processar {url_alvo}: {e}")

    if encontrados == 0:
        enviar_alerta_telegram(
            f"🔍 *Varredura Real Concluída - {horario_atual}*\n\n"
            f"O robô varreu os portais de Itatiba e Jundiaí com sucesso. Nenhum lote novo nominado na região nesta rodada, mas seguimos monitorando!"
        )
    else:
        print(f"Total de {encontrados} lotes enviados com sucesso nesta execução.")


if __name__ == "__main__":
    executar_varredura_real()
