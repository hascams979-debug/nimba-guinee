
import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

raw_key = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_KEY = raw_key.strip().replace('"', '').replace("'", "")

SYSTEM_PROMPT = """
Tu es NIMBA AI, la première Intelligence Artificielle éducative, technique et patriotique de la République de Guinée (Conakry).
Ton symbole est le masque Nimba (D'mba), symbole universel de sagesse, de travail et de générosité.
Ta devise est : Travail - Justice - Solidarité.
Tu aides la jeunesse et les professionnels guinéens avec bienveillance et clarté.
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NIMBA AI - L'IA de la Guinée</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: #0f172a; color: #f8fafc; display: flex; flex-direction: column; height: 100vh; }
        .flag-bar { display: flex; height: 6px; width: 100%; }
        .flag-red { background: #ce1126; flex: 1; }
        .flag-yellow { background: #fcd116; flex: 1; }
        .flag-green { background: #009460; flex: 1; }
        header { background: #1e293b; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #334155; }
        #chat-container { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
        .msg { max-width: 85%; padding: 12px 16px; border-radius: 18px; line-height: 1.45; font-size: 15px; word-wrap: break-word; }
        .bot { background: #1e293b; align-self: flex-start; border: 1px solid #334155; color: #f1f5f9; }
        .user { background: #009460; color: white; align-self: flex-end; }
        #input-container { background: #1e293b; padding: 10px 14px; display: flex; gap: 8px; align-items: center; border-top: 1px solid #334155; }
        #user-input { flex: 1; background: #0f172a; border: 1px solid #475569; color: white; padding: 12px 16px; border-radius: 25px; font-size: 15px; outline: none; }
        .btn-send { background: #009460; color: white; border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; font-size: 18px; }
    </style>
</head>
<body>
    <div class="flag-bar"><div class="flag-red"></div><div class="flag-yellow"></div><div class="flag-green"></div></div>
    <header>
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:26px;">🇬🇳</span>
            <div><h1 style="font-size:16px;">NIMBA AI</h1><p style="font-size:11px; color:#94a3b8;">Tuteur National de Guinée</p></div>
        </div>
    </header>
    <div id="chat-container">
        <div class="msg bot">I ni sogoma ! Je suis <b>NIMBA AI</b> 🇬🇳. Pose-moi une question pour tester la connexion !</div>
    </div>
    <div id="input-container">
        <input type="text" id="user-input" placeholder="Pose ta question..." onkeypress="if(event.key==='Enter') envoyerMessage()">
        <button class="btn-send" onclick="envoyerMessage()">➤</button>
    </div>
    <script>
        const chat = document.getElementById('chat-container');
        const input = document.getElementById('user-input');

        async function envoyerMessage() {
            const msg = input.value.trim();
            if (!msg) return;
            chat.innerHTML += `<div class="msg user">${msg}</div>`;
            input.value = '';
            const loadId = "load-" + Date.now();
            chat.innerHTML += `<div id="${loadId}" class="msg bot" style="color:#94a3b8;">NIMBA interroge le cerveau...</div>`;
            chat.scrollTop = chat.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg })
                });
                const data = await res.json();
                document.getElementById(loadId).remove();
                chat.innerHTML += `<div class="msg bot">${data.reply}</div>`;
                chat.scrollTop = chat.scrollHeight;
            } catch (err) {
                document.getElementById(loadId).remove();
                chat.innerHTML += `<div class="msg bot" style="color:#ef4444;">Erreur locale navigateur.</div>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    donnees = request.get_json() or {}
    message_utilisateur = donnees.get("message", "").strip()

    if not message_utilisateur:
        return jsonify({"reply": "Écris-moi une question !"})

    if not GEMINI_API_KEY:
        return jsonify({"reply": "⚠️ ERREUR : La variable GEMINI_API_KEY est VIDE dans Render !"})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [
            {
                "parts": [{"text": f"{SYSTEM_PROMPT}\n\nQuestion : {message_utilisateur}"}]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=20)
        if response.status_code == 200:
            resultat = response.json()
            texte = resultat["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"reply": texte.replace("\n", "<br>")})
        else:
            # ICI LE VRAI DIAGNOSTIC DE GOOGLE :
            return jsonify({"reply": f"🔍 <b>DIAGNOSTIC GOOGLE :</b><br>Code : {response.status_code}<br>Détail : {response.text[:250]}"})
    except Exception as e:
        return jsonify({"reply": f"⚠️ Erreur Exception : {str(e)[:150]}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
