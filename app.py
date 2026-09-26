import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==== CONFIGURAÇÕES (pegue no Meta for Developers) ====
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "123456")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "EAAapx5KgzoMBSmZCp0RlVhaelHFhFz0ZA2QcUZAvlRwmcUyVRNHPRQEuqvWTZCcXwaB7nGDx2w6FKxkPVPQjUyPdOIZCKEnE3326RCvSDYmCkgbBomErdGNqlIafszD8WnTkq1OQ2pklSVd6D56NLxjXwTadazZBMg8uJ692ZCsZCHnQAINxB69QpBWGbKMSQcNyL15z8lFsEQO4UP0fUoVOVlZBbhCqQmdBwtGxJLNBdLxaYNIN9Y8XqyhIjmsDVZAxlG8RQYzJKq1LlrZAciIp65gKNK1")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "1375650348961601")

GRAPH_API_URL = curl -i -X POST `
     https://graph.facebook.com/v25.0/1375650348961601/messages `
     -H 'Authorization: Bearer EAAapx5KgzoMBSmZCp0RlVhaelHFhFz0ZA2QcUZAvlRwmcUyVRNHPRQEuqvWTZCcXwaB7nGDx2w6FKxkPVPQjUyPdOIZCKEnE3326RCvSDYmCkgbBomErdGNqlIafszD8WnTkq1OQ2pklSVd6D56NLxjXwTadazZBMg8uJ692ZCsZCHnQAINxB69QpBWGbKMSQcNyL15z8lFsEQO4UP0fUoVOVlZBbhCqQmdBwtGxJLNBdLxaYNIN9Y8XqyhIjmsDVZAxlG8RQYzJKq1LlrZAciIp65gKNK1' `
     -H 'Content-Type: application/json' `
     -d '{ \"messaging_product\": \"whatsapp\",
     \"to\": \"5511967620340\",
     \"type\": \"template\",
     \"template\": { \"name\": \"jaspers_market_order_confirmation_v1\",
     \"language\": { \"code\": \"en_US\" },
     \"components\": [{ \"type\": \"body\", \"parameters\": [{ \"type\": \"text\", \"text\": \"John Doe\" }, { \"type\": \"text\", \"text\": \"123456\" }, { \"type\": \"text\", \"text\": \"Sep 26, 2026\" }] }] } }'

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
            from_number = message["from"]  # número de quem enviou
            msg_type = message["type"]

            if msg_type == "text":
                texto_recebido = message["text"]["body"]
                resposta = gerar_resposta(texto_recebido)
                enviar_mensagem(from_number, resposta)

    except (KeyError, IndexError, TypeError):
        # Payload não continha uma mensagem (ex: status de entrega, leitura, etc.)
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
