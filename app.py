import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Nettoyage automatique de la clé d'API (supprime les espaces et guillemets)
raw_key = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_KEY = raw_key.strip().replace('"', '').replace("'", "")

SYSTEM_PROMPT = """
Tu es NIMBA AI, la première Intelligence Artificielle éducative, technique et patriotique de la République de Guinée (Conakry).
Ton symbole est le masque Nimba (D'mba), symbole universel de sagesse, de travail et de générosité.
Ta devise est : Travail - Justice - Solidarité.

Tes rôles fondamentaux pour la jeunesse et le peuple de Guinée :
1. TUTEUR SCOLAIRE & UNIVERSITAIRE : Tu expliques avec clarté, bienveillance et rigueur les cours du collège au lycée (Mathématiques, Physique-Chimie, Français, Philosophie, SVT) et de l'université.
2. EXPERT FORMATION PROFESSIONNELLE & MÉTIERS (CFP) : Tu es un guide pratique pour les élèves des écoles techniques et professionnelles (Mécanique auto/engins, Électricité bâtiment, Plomberie, Santé communautaire/soins infirmiers, Maçonnerie, Menuiserie, Agronomie). Tu donnes des diagnostics de pannes, des dosages de chantiers, des schémas explicatifs et des conseils de sécurité.
3. CULTURE & HISTOIRE DE LA GUINÉE : Tu connais parfaitement l'histoire glorieuse de la Guinée (le 28 septembre 1958, le non historique à De Gaulle, Samory Touré, les 4 régions naturelles : Basse Guinée, Moyenne Guinée, Haute Guinée, Guinée Forestière, et les grands projets comme Simandou).
4. ENTREPRENEURIAT & GESTION : Tu aides les artisans et commerçants à calculer leurs marges, rédiger des devis propres et des factures en Francs Guinéens (GNF).

Style de communication :
- Chaleureux, encourageant, respectueux et digne d'un grand frère ou précepteur guinéen.
- Si l'utilisateur te salue dans une langue nationale (I ni sogoma, Tana alama, Inwali, etc.), réponds chaleureusement avec respect.
- Tes explications doivent être simples, directes et faciles à comprendre sur un écran de téléphone.
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
        .header-title { display: flex; align-items: center; gap: 10px; }
        .badge { background: #ce1126; color: white; font-size: 11px; font-weight: bold; padding: 2px 8px; border-radius: 12px; }
        
        #chat-container { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
        
        .msg { max-width: 85%; padding: 12px 16px; border-radius: 18px; line-height: 1.45; font-size: 15px; word-wrap: break-word; }
        .bot { background: #1e293b; align-self: flex-start; border: 1px solid #334155; color: #f1f5f9; border-bottom-left-radius: 4px; }
        .user { background: #009460; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
        
        .suggestions { display: flex; gap: 8px; overflow-x: auto; padding: 8px 16px; background: #0f172a; scrollbar-width: none; }
        .suggestion-btn { background: #1e293b; color: #cbd5e1; border: 1px solid #475569; padding: 6px 12px; border-radius: 20px; font-size: 12px; white-space: nowrap; cursor: pointer; }
        
        #input-container { background: #1e293b; padding: 10px 14px; display: flex; gap: 8px; align-items: center; border-top: 1px solid #334155; }
        #user-input { flex: 1; background: #0f172a; border: 1px solid #475569; color: white; padding: 12px 16px; border-radius: 25px; font-size: 15px; outline: none; }
        
        .btn-action { background: #ce1126; color: white; border: none; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 18px; }
        .btn-voice { background: #fcd116; color: #0f172a; }
        .btn-send { background: #009460; }
    </style>
</head>
<body>
    <div class="flag-bar">
        <div class="flag-red"></div>
        <div class="flag-yellow"></div>
        <div class="flag-green"></div>
    </div>

    <header>
        <div class="header-title">
            <span style="font-size: 26px;">🇬🇳</span>
            <div>
                <h1 style="font-size: 16px; font-weight: 800; letter-spacing: 0.5px;">NIMBA AI</h1>
                <p style="font-size: 11px; color: #94a3b8;">Tuteur National & Conseiller Pratique</p>
            </div>
        </div>
        <span class="badge">GUINÉE v1.0</span>
    </header>

    <div id="chat-container">
        <div class="msg bot">
            I ni sogoma ! Salut mon frère / ma sœur 🇬🇳<br><br>
            Je suis <b>NIMBA AI</b>, l'intelligence artificielle au service de la jeunesse et des professionnels de Guinée.<br><br>
            Comment puis-je t'aider aujourd'hui ?
            <ul style="margin: 8px 0 0 16px; font-size: 13px;">
                <li>📚 Réviser un cours (Collège, Lycée, Université)</li>
                <li>🔧 Résoudre une panne ou un calcul de chantier (CFP / Métiers)</li>
                <li>🇬🇳 Découvrir l'histoire et les richesses de la Guinée</li>
                <li>💼 Rédiger un devis ou gérer ton atelier</li>
            </ul>
        </div>
    </div>

    <div class="suggestions">
        <button class="suggestion-btn" onclick="poserQuestion('Explique-moi le théorème de Thalès avec un exemple simple.')">📐 Maths : Thalès</button>
        <button class="suggestion-btn" onclick="poserQuestion('Un moteur diesel claque et fume noir. Quelles sont les causes mécaniques possibles ?')">🔧 Diagnostic Mécanique</button>
        <button class="suggestion-btn" onclick="poserQuestion('Comment doser le béton pour couler un poteau solide en Guinée ?')">🏗️ Dosage Béton</button>
        <button class="suggestion-btn" onclick="poserQuestion('Raconte-moi ce qui s\\'est passé le 28 septembre 1958 en Guinée.')">🇬🇳 Histoire du 28 Septembre</button>
    </div>

    <div id="input-container">
        <button id="voice-btn" class="btn-action btn-voice" onclick="toggleVoix()" title="Parler avec la voix">🎙️</button>
        <input type="text" id="user-input" placeholder="Pose ta question à NIMBA..." onkeypress="handleKey(event)">
        <button class="btn-action btn-send" onclick="envoyerMessage()" title="Envoyer">➤</button>
    </div>

    <script>
        const chat = document.getElementById('chat-container');
        const input = document.getElementById('user-input');
        const voiceBtn = document.getElementById('voice-btn');
        let recognition = null;
        let ecouteActive = false;

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRec();
            recognition.lang = 'fr-FR';
            recognition.continuous = false;
            
            recognition.onresult = (e) => {
                const texte = e.results[0][0].transcript;
                input.value = texte;
                envoyerMessage();
                arreterMicro();
            };
            recognition.onerror = () => arreterMicro();
            recognition.onend = () => arreterMicro();
        }

        function toggleVoix() {
            if (!recognition) {
                alert("La commande vocale n'est pas supportée sur ce navigateur. Utilise Google Chrome !");
                return;
            }
            if (!ecouteActive) {
                recognition.start();
                ecouteActive = true;
                voiceBtn.style.background = "#ce1126";
                voiceBtn.innerText = "🛑";
                input.placeholder = "Nimba t'écoute... Parle maintenant !";
            } else {
                arreterMicro();
            }
        }

        function arreterMicro() {
            if (recognition) recognition.stop();
            ecouteActive = false;
            voiceBtn.style.background = "#fcd116";
            voiceBtn.innerText = "🎙️";
            input.placeholder = "Pose ta question à NIMBA...";
        }

        function parlerReponse(texte) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const cleanText = texte.replace(/<[^>]*>?/gm, '');
                const utterance = new SpeechSynthesisUtterance(cleanText);
                utterance.lang = 'fr-FR';
                utterance.rate = 1.0;
                window.speechSynthesis.speak(utterance);
            }
        }

        function poserQuestion(texte) {
            input.value = texte;
            envoyerMessage();
        }

        function handleKey(e) {
            if (e.key === 'Enter') envoyerMessage();
        }

        async function envoyerMessage() {
            const msg = input.value.trim();
            if (!msg) return;

            chat.innerHTML += `<div class="msg user">${msg}</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;

            const loadingId = "load-" + Date.now();
            chat.innerHTML += `<div id="${loadingId}" class="msg bot" style="color: #94a3b8;">NIMBA réfléchit... 🇬🇳</div>`;
            chat.scrollTop = chat.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg })
                });
                const data = await res.json();
                document.getElementById(loadingId).remove();
                
                chat.innerHTML += `<div class="msg bot">${data.reply}</div>`;
                chat.scrollTop = chat.scrollHeight;
                
                parlerReponse(data.reply);
            } catch (err) {
                document.getElementById(loadingId).remove();
                chat.innerHTML += `<div class="msg bot" style="color:#ef4444;">Désolé, problème de connexion avec le serveur. Réessaie !</div>`;
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
        return jsonify({"reply": "Pose-moi une question, je suis là pour toi !"})

    if not GEMINI_API_KEY:
        return jsonify({"reply": "⚠️ La clé d'intelligence n'est pas encore enregistrée dans Render."})

    # Liste des modèles Google testés dans l'ordre pour garantir une réponse sans erreur 404
    modeles = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    texte_complet = f"{SYSTEM_PROMPT}\n\nQUESTION DE L'UTILISATEUR GUINÉEN :\n{message_utilisateur}"
    payload = {
        "contents": [
            {
                "parts": [{"text": texte_complet}]
            }
        ]
    }

    dernier_code = 0
    for modele in modeles:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modele}:generateContent?key={GEMINI_API_KEY}"
        try:
            response = requests.post(url, json=payload, timeout=20)
            dernier_code = response.status_code
            if response.status_code == 200:
                resultat = response.json()
                texte_brut = resultat["candidates"][0]["content"]["parts"][0]["text"]
                texte_formate = texte_brut.replace("\n", "<br>").replace("**", "<b>").replace("*", "•")
                return jsonify({"reply": texte_formate})
        except Exception:
            continue

    return jsonify({"reply": f"⚠️ Connexion au cerveau en cours de validation (Code {dernier_code}). Réessaie dans quelques secondes !"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
