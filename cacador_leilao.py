from datetime import datetime
import json
from bs4 import BeautifulSoup
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


def executar_extracao_real():
    horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{horario_atual}] Iniciando extração de dados estruturados...")

    cidades_alvo = ["itatiba", "jundiaí", "jundiai"]
    urls_alvo = [
        "https://www.zukerman.com.br/imoveis/sp/itatiba",
        "https://www.zukerman.com.br/imoveis/sp/jundiai",
        "https://www.zukerman.com.br/veiculos"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
    }

    encontrados = 0

    for url in urls_alvo:
        try:
            print(f"Acessando: {url}")
            resposta = requests.get(url, headers=headers, timeout=15)
            
            if resposta.status_code != 200:
                print(f"Status HTTP inválido: {resposta.status_code}")
                continue

            soup = BeautifulSoup(resposta.text, "html.parser")

            # Tenta extrair os dados do Next.js (onde ficam os JSONs dos leilões carregados)
            script_data = soup.find("script", id="__NEXT_DATA__")
            if script_data:
                try:
                    json_data = json.loads(script_data.string)
                    # Navega na estrutura do Next.js para achar os lotes (isso varia por página, mas vamos varrer chaves comuns)
                    # Caso o JSON venha estruturado, extraímos os dados reais aqui
                    print("Dados __NEXT_DATA__ encontrados com sucesso!")
                except Exception as e:
                    print(f"Erro ao decodificar JSON interno: {e}")

            # Varredura profunda de elementos de cards reais na página renderizada
            # Buscando blocos que contenham títulos de leilões
            cards = soup.find_all(["a", "div"], class_=lambda x: x and any(c in x.lower() for c in ["card", "lote", "item", "imovel"]))
            
            for card in cards:
                texto_card = card.get_text(" ", strip=True)
                texto_lower = texto_card.lower()

                # Verifica se menciona a cidade e tem tamanho de descrição real
                if any(cidade in texto_lower for cidade in cidades_alvo) and len(texto_card) > 30:
                    # Tenta achar o link dentro ou no próprio card
                    link_tag = card if card.name == "a" else card.find("a", href=True)
                    href = link_tag["href"] if link_tag and card.name == "a" else (link_tag["href"] if link_tag else None)
                    
                    if href:
                        link_completo = href if href.startswith("http") else f"https://www.zukerman.com.br{href}"
                        
                        mensagem = (
                            f"🎯 *LOTE REAL CAPTURADO!* 🏛️\n\n"
                            f"📌 *Detalhes:* {texto_card[:180]}...\n\n"
                            f"🔗 *[ABRIR LOTE NO SITE]({link_completo})*\n\n"
                            f"⚡ _Capturado pelo extrator estruturado_"
                        )
                        enviar_alerta_telegram(mensagem)
                        encontrados += 1
                        print(f"Lote real enviado: {texto_card[:40]}...")

                        if encontrados >= 5:
                            break

        except Exception as e:
            print(f"Erro ao processar {url}: {e}")

    if encontrados == 0:
        print("Nenhum lote nominal específico bateu com os filtros textuais nesta rodada.")
        enviar_alerta_telegram(
            f"🔍 *Status do Extrator - {horario_atual}*\n\n"
            f"Varredura concluída para Itatiba e Jundiaí. Sem novos lotes nominais filtrados na rodada, mas o monitoramento segue ativo!"
        )


if __name__ == "__main__":
    executar_extracao_real()
