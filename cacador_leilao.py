from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup

# ======================================================
# CONFIGURAÇÕES
# ======================================================
TELEGRAM_TOKEN = "9245271479:AAFyUOHNCCMhZDZceyHYYv4AsbRv1iwZa4E"
TELEGRAM_CHAT_ID = "302880433"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")


def enviar_telegram(mensagem):
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


def criar_github_issue(titulo, corpo):
    if not GITHUB_TOKEN or not GITHUB_REPOSITORY:
        print("Token ou Repositório do GitHub não encontrados para criar a Issue.")
        return

    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/issues"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "title": titulo,
        "body": corpo,
        "labels": ["leilao", "oportunidade"],
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 201:
            print(f"Issue criada com sucesso no GitHub: {titulo}")
        else:
            print(f"Erro ao criar Issue: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Erro na requisição da Issue: {e}")


def executar_cacador():
    horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{horario_atual}] Iniciando varredura com integração de Issues...")

    # Alvos principais para Itatiba, Jundiaí e Veículos
    alvos = [
        {"nome": "Zukerman - Imóveis Itatiba", "url": "https://www.zukerman.com.br/imoveis/sp/itatiba", "cidade": "Itatiba"},
        {"nome": "Zukerman - Imóveis Jundiaí", "url": "https://www.zukerman.com.br/imoveis/sp/jundiai", "cidade": "Jundiaí"},
        {"nome": "Zukerman - Veículos", "url": "https://www.zukerman.com.br/veiculos", "cidade": "Regional/SP"}
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
    }

    encontrados = 0

    for alvo in alvos:
        try:
            print(f"Consultando {alvo['nome']}...")
            resp = requests.get(alvo["url"], headers=headers, timeout=15)
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Coleta links de lotes/imóveis/veículos específicos na página
                links_unicos = set()
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    texto = a.get_text(strip=True)
                    if any(termo in href for termo in ["/imovel/", "/lote/", "/veiculo/"]) and len(texto) > 10:
                        link_completo = href if href.startswith("http") else f"https://www.zukerman.com.br{href}"
                        links_unicos.add((texto, link_completo))

                # Se achar itens específicos, processa
                for titulo_lote, link_lote in list(links_unicos)[:3]:
                    encontrados += 1
                    msg_telegram = (
                        f"🎯 *OPORTUNIDADE DE LEILÃO!* 🏛️\n\n"
                        f"📍 *Região:* {alvo['cidade']}\n"
                        f"📌 *Item:* {titulo_lote}\n\n"
                        f"🔗 *[ACESSAR LOTE DIRETAMENTE]({link_lote})*\n\n"
                        f"⚡ _Capturado em {horario_atual}_"
                    )
                    enviar_telegram(msg_telegram)

                    # Cria Issue no GitHub para cada lote encontrado
                    issue_titulo = f"[{alvo['cidade']}] {titulo_lote[:60]}"
                    issue_corpo = (
                        f"### Oportunidade Detectada pelo Robô\n\n"
                        f"- **Portal:** {alvo['nome']}\n"
                        f"- **Cidade Alvo:** {alvo['cidade']}\n"
                        f"- **Descrição:** {titulo_lote}\n"
                        f"- **Link Direto:** [{link_lote}]({link_lote})\n"
                        f"- **Data/Hora:** {horario_atual}\n"
                    )
                    criar_github_issue(issue_titulo, issue_corpo)

        except Exception as e:
            print(f"Erro ao processar {alvo['nome']}: {e}")

    # Se não houver lotes filtrados por texto específico nesta rodada, abre uma Issue de status e avisa no Telegram com o link de busca direta
    if encontrados == 0:
        for alvo in alvos:
            msg_status = (
                f"🔍 *BUSCA REGIONAL - {horario_atual}*\n\n"
                f"🏛️ *Portal:* {alvo['nome']}\n"
                f"🔗 *[ABRIR FILTRO OFICIAL NO SITE]({alvo['url']})*\n\n"
                f"⚡ _Nenhum lote nominal na janela atual. Use o link para conferir._"
            )
            enviar_telegram(msg_status)
            
            # Cria Issue de acompanhamento da varredura
            criar_github_issue(
                f"Varredura Sem Lotes Novos - {alvo['cidade']} ({datetime.now().strftime('%d/%m/%Y')})",
                f"O robô executou a varredura em {alvo['nome']} ({alvo['url']}) em {horario_atual}, mas não encontrou novos lotes nominais na listagem estática. O link de acesso direto permanece monitorado."
            )

    print(f"Varredura finalizada. Total de ações executadas: {encontrados}")


if __name__ == "__main__":
    executar_cacador()
