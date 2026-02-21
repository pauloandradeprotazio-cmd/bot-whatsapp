from flask import Flask, request, jsonify
from google import genai
from google.genai import types
import requests
import os

app = Flask(__name__)

WHATSAPP_TOKEN  = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")
VERIFY_TOKEN    = os.environ.get("VERIFY_TOKEN", "meu_bot_secreto_123")
GEMINI_APIKEY   = os.environ.get("GEMINI_APIKEY", "")

PERSONALIDADE = (
    "Voce e a assistente virtual da loja XYZ chamada Lia. "
    "Responda SEMPRE em portugues brasileiro, simpatica e objetiva. "
    "Produtos: Camisetas R$50, Calcas R$100, Tenis R$200. "
    "Horario: Seg a Sex 8h as 18h, Sab 8h as 13h. "
    "Entrega: ate 7 dias uteis, frete gratis acima de R$150. "
    "Pagamentos: PIX, cartao credito ate 12x, boleto. "
    "Respostas curtas maximo 4 linhas. "
    "Nunca invente informacoes."
)

client = genai.Client(api_key=GEMINI_APIKEY)
historicos = {}

def perguntar_gemini(numero, mensagem):
    if numero not in historicos:
        historicos[numero] = []
    historicos[numero].append(
        types.Content(role="user", parts=[types.Part(text=mensagem)])
    )
    try:
        resposta = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(system_instruction=PERSONALIDADE),
            contents=historicos[numero]
        )
        texto = resposta.text.strip()
        historicos[numero].append(
            types.Content(role="model", parts=[types.Part(text=texto)])
        )
        return texto
    except Exception as e:
        print("[GEMINI ERRO] " + str(e))
        return "Desculpe, tive um problema. Tente novamente!"

def enviar_mensagem(numero, texto):
    url = "https://graph.facebook.com/v19.0/" + PHONE_NUMBER_ID + "/messages"
    headers = {
        "Authorization": "Bearer " + WHATSAPP_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    try:
        r = requests.post(url, headers=headers, json=payload)
        print("[ENVIADO " + str(r.status_code) + "] Para " + numero)
    except Exception as e:
        print("[ERRO ENVIO] " + str(e))

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("[WEBHOOK] Verificado!")
        return challenge, 200
    return "Token invalido", 403

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    data = request.json
    try:
        changes = data["entry"][0]["changes"][0]["value"]
        if "messages" not in changes:
            return jsonify({"status": "ok"}), 200
        msg    = changes["messages"][0]
        numero = msg["from"]
        tipo   = msg["type"]
        if tipo == "text":
            texto = msg["text"]["body"]
            print("[MSG de " + numero + "] " + texto)
            resposta = perguntar_gemini(numero, texto)
            print("[GEMINI] " + resposta)
            enviar_mensagem(numero, resposta)
        else:
            enviar_mensagem(numero, "Processo apenas texto. Como posso ajudar?")
    except Exception as e:
        print("[ERRO] " + str(e))
    return jsonify({"status": "ok"}), 200

@app.route("/", methods=["GET"])
def status():
    return jsonify({"status": "Bot online!", "conversas": len(historicos)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```

---
