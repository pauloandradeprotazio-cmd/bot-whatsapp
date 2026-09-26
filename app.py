import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==== CONFIGURAÇÕES (pegue no Meta for Developers) ====
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "meu_token_secreto")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "SEU_ACCESS_TOKEN_AQUI")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "SEU_PHONE_NUMBER_ID_AQUI")

GRAPH_API_URL = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Meta chama essa rota uma vez para validar seu servidor."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Token inválido", 403


@app.route("/webhook", methods=["POST"])
def receive_message():
    """Recebe mensagens enviadas pelos usuários no WhatsApp."""
    data = request.get_json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" in value:
            message = value["messages"][0]
            from_number = message["from"]
            msg_type = message["type"]

            if msg_type == "text":
                texto_recebido = message["text"]["body"]
                resposta = gerar_resposta(texto_recebido)
                enviar_mensagem(from_number, resposta)

    except (KeyError, IndexError, TypeError):
        pass

    return jsonify({"status": "ok"}), 200


def gerar_resposta(texto_usuario: str) -> str:
    """Lógica simples do bot. Troque por regras mais elaboradas ou IA."""
    texto = texto_usuario.lower().strip()

    if texto in ("oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"):
        return "Olá! 👋 Sou o assistente virtual. Como posso ajudar?\n\n1. Horário de funcionamento\n2. Falar com atendente\n3. Ver produtos"
    elif texto == "1":
        return "Funcionamos de segunda a sexta, das 9h às 18h."
    elif texto == "2":
        return "Certo! Já vou te transferir para um atendente humano."
    elif texto == "3":
        return "Aqui estão nossos produtos: [link do catálogo]"
    else:
        return "Não entendi 🤔. Digite *1*, *2* ou *3* para ver as opções."


def enviar_mensagem(numero_destino: str, texto: str):
    """Envia uma mensagem de texto via WhatsApp Cloud API."""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto},
    }
    response = requests.post(GRAPH_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print("Erro ao enviar mensagem:", response.text)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
