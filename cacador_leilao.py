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


def executar_varredura_direta():
    horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{horario_atual}] Iniciando varredura inteligente de leilões...")

    # Vamos monitorar diretamente as páginas oficiais de busca por região/imóveis/veículos
    alvos = [
        {"nome": "Zukerman - Imóveis Itatiba", "url": "https://www.zukerman.com.br/imoveis/sp/itatiba"},
        {"nome": "Zukerman - Imóveis Jundiaí", "url": "https://www.zukerman.com.br/imoveis/sp/jundiai"},
        {"nome": "Zukerman - Veículos SP", "url": "https://www.zukerman.com.br/veiculos"}
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    total_enviados = 0

    for alvo in alvos:
        print(f"Consultando: {alvo['nome']} ({alvo['url']})")
        try:
            resposta = requests.get(alvo["url"], headers=headers, timeout=15)
            
            if resposta.status_code == 200:
                soup = BeautifulSoup(resposta.text, "html.parser")
                
                # Como o HTML estático pode vir enxuto, vamos buscar qualquer link de card ou detalhe de lote
                links_encontrados = set()
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    texto = a.get_text(strip=True)
                    
                    # Filtra apenas links que parecem ser de lotes/imóveis/veículos específicos
                    if ("/imovel/" in href or "/lote/" in href or "/veiculo/" in href) and len(texto) > 10:
                        link_completo = href if href.startswith("http") else f"https://www.zukerman.com.br{href}"
                        links_encontrados.add((texto, link_completo))

                print(f"Encontrados {len(links_encontrados)} links potenciais em {alvo['nome']}.")

                # Envia os links encontrados para o Telegram
                for titulo, link in list(links_encontrados)[:5]: # Limita aos 5 primeiros por alvo
                    mensagem = (
                        f"🎯 *OPORTUNIDADE CAPTURADA!* 🏛️\n\n"
                        f"📍 *Origem:* {alvo['nome']}\n"
                        f"📌 *Item:* {titulo}\n\n"
                        f"🔗 *[ACESSAR LOTE DIRETAMENTE]({link})*\n\n"
                        f"⚡ _Atualizado em {horario_atual}_"
                    )
                    enviar_alerta_telegram(mensagem)
                    total_enviados += 1
            else:
                print(f"Erro HTTP {resposta.status_code} em {alvo['nome']}")

        except Exception as e:
            print(f"Erro ao processar {alvo['nome']}: {e}")

    # Se mesmo assim não achar nada pelos filtros de texto, manda o link direto de acesso das buscas regionais para você conferir com 1 clique
    if total_enviados == 0:
        for alvo in alvos:
            mensagem = (
                f"🔍 *BUSCA DIRETA REGIONAL - {horario_atual}*\n\n"
                f"🏛️ *Portal:* {alvo['nome']}\n"
                f"🔗 *[ABRIR FILTRO DA REGIÃO NO SITE]({alvo['url']})*\n\n"
                f"⚡ _Acesse para conferir os lotes ativos no momento._"
            )
            enviar_alerta_telegram(mensagem)
    else:
        print(f"Total de {total_enviados} alertas enviados com sucesso.")


if __name__ == "__main__":
    executar_varredura_direta()
