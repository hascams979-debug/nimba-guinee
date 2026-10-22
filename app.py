import os, requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
KEY = os.environ.get("GEMINI_API_KEY", "").strip().replace('"', '').replace("'", "")

SYSTEM = """Tu es NIMBA AI, l'IA éducative et patriotique de Guinée (Conakry).
Symbole : masque Nimba. Devise : Travail - Justice - Solidarité.
Missions :
1. Tuteur scolaire (Collège, Lycée, Université).
2. CFP & Écoles Professionnelles : Mécanique auto/engins, Électricité, Chantiers/Béton, Santé communautaire. Diagnostic de pannes et dosages.
3. Histoire de Guinée (28 sept 1958, régions, Simandou).
Style : Grand frère guinéen bienveillant, clair et encourageant. Salue chaleureusement si on te parle en langues locales."""

HTML = """<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>NIMBA AI 🇬🇳</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:system-ui,-apple-system,sans-serif}
body{background:#0f172a;color:#fff;display:flex;flex-direction:column;height:100vh}
.flag{display:flex;height:6px}.r{background:#ce1126;flex:1}.y{background:#fcd116;flex:1}.g{background:#009460;flex:1}
header{background:#1e293b;padding:12px 16px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #334155}
#chat{flex:1;overflow-y:auto;padding:15px;display:flex;flex-direction:column;gap:10px}
.msg{max-width:85%;padding:10px 14px;border-radius:15px;font-size:15px;line-height:1.4}
.b{background:#1e293b;align-self:flex-start;border:1px solid #334155}
.u{background:#009460;align-self:flex-end}
.quick{display:flex;gap:8px;overflow-x:auto;padding:8px 15px;background:#0f172a}
.qb{background:#1e293b;color:#cbd5e1;border:1px solid #475569;padding:6px 12px;border-radius:20px;font-size:12px;white-space:nowrap;cursor:pointer}
.bar{background:#1e293b;padding:10px;display:flex;gap:8px;border-top:1px solid #334155}
input{flex:1;background:#0f172a;border:1px solid #475569;color:#fff;padding:10px 15px;border-radius:20px;outline:none;font-size:15px}
.btn{width:42px;height:42px;border-radius:50%;border:none;cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center}
.mic{background:#fcd116;color:#000}.send{background:#009460;color:#fff}
</style></head>
<body>
<div class="flag"><div class="r"></div><div class="y"></div><div class="g"></div></div>
<header>
<div style="display:flex;align-items:center;gap:8px"><span style="font-size:24px">🇬🇳</span><div><h1 style="font-size:15px">NIMBA AI</h1><p style="font-size:10px;color:#94a3b8">Éducation & Formation Pro (CFP)</p></div></div>
<span style="background:#ce1126;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:bold">GUINÉE</span>
</header>
<div id="chat">
<div class="msg b">I ni sogoma ! Salut mon frère / ma sœur 🇬🇳<br>Je suis <b>NIMBA AI</b>, l'intelligence artificielle au service des élèves, étudiants et professionnels de Guinée.<br><br>Pose-moi une question sur tes cours, une panne mécanique, un chantier ou l'histoire du pays !</div>
</div>
<div class="quick">
<button class="qb" onclick="q('Explique le théorème de Thalès simplement avec un exemple.')">📐 Maths : Thalès</button>
<button class="qb" onclick="q('Diagnostic panne : moteur diesel qui claque et fume noir.')">🔧 Mécanique (CFP)</button>
<button class="qb" onclick="q('Quel est le dosage de béton pour couler un poteau en Guinée ?')">🏗️ Dosage Chantier</button>
<button class="qb" onclick="q('Raconte l histoire du 28 septembre 1958 en Guinée.')">🇬🇳 Histoire de Guinée</button>
</div>
<div class="bar">
<button id="mb" class="btn mic" onclick="v()">🎙️</button>
<input type="text" id="in" placeholder="Pose ta question à NIMBA..." onkeypress="if(event.key==='Enter')s()">
<button class="btn send" onclick="s()">➤</button>
</div>
<script>
const c=document.getElementById('chat'),i=document.getElementById('in'),mb=document.getElementById('mb');
let rec=null,sp=false;
if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
rec=new SR();rec.lang='fr-FR';
rec.onresult=(e)=>{i.value=e.results[0][0].transcript;s();stopV();};
rec.onerror=()=>stopV();rec.onend=()=>stopV();
}
function v(){
if(!rec){alert("Micro non disponible sur ce navigateur. Utilise Chrome !");return;}
if(!sp){rec.start();sp=true;mb.style.background="#ce1126";mb.innerText="🛑";i.placeholder="Parle maintenant...";}else{stopV();}
}
function stopV(){if(rec)rec.stop();sp=false;mb.style.background="#fcd116";mb.innerText="🎙️";i.placeholder="Pose ta question à NIMBA...";}
function speak(t){
if('speechSynthesis' in window){
window.speechSynthesis.cancel();
const u=new SpeechSynthesisUtterance(t.replace(/<[^>]*>?/gm,''));
u.lang='fr-FR';window.speechSynthesis.speak(u);
}
}
function q(t){i.value=t;s();}
async function s(){
const m=i.value.trim();if(!m)return;
c.innerHTML+=`<div class="msg u">${m}</div>`;i.value='';c.scrollTop=c.scrollHeight;
const lid="l"+Date.now();
c.innerHTML+=`<div id="${lid}" class="msg b" style="color:#94a3b8">NIMBA réfléchit... 🇬🇳</div>`;c.scrollTop=c.scrollHeight;
try{
const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({msg:m})});
const d=await r.json();document.getElementById(lid).remove();
c.innerHTML+=`<div class="msg b">${d.reply}</div>`;c.scrollTop=c.scrollHeight;
speak(d.reply);
}catch(e){
document.getElementById(lid).remove();
c.innerHTML+=`<div class="msg b" style="color:#ef4444">Erreur de connexion. Réessaie !</div>`;
}
}
</script></body></html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = (request.get_json() or {}).get("msg", "").strip()
    if not user_msg:
        return jsonify({"reply": "Pose-moi une question !"})
    if not KEY:
        return jsonify({"reply": "⚠️ Clé API manquante dans Render."})

    try:
        # 1. Demande automatique à Google des modèles actifs pour ta clé
        m_res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={KEY}", timeout=10)
        if m_res.status_code != 200:
            return jsonify({"reply": f"⚠️ Clé refusée par Google ({m_res.status_code}) : {m_res.text[:150]}"})

        liste = m_res.json().get("models", [])
        modele_choisi = None

        # Cherche le meilleur modèle moderne (flash ou compatible generateContent)
        for m in liste:
            nom = m.get("name", "")
            methodes = m.get("supportedGenerationMethods", [])
            if "generateContent" in methodes:
                if "flash" in nom:
                    modele_choisi = nom
                    break
                elif not modele_choisi:
                    modele_choisi = nom

        if not modele_choisi:
            return jsonify({"reply": "⚠️ Aucun modèle d'intelligence actif sur ce compte Google."})

        # 2. Appel au modèle officiel validé par Google
        url = f"https://generativelanguage.googleapis.com/v1beta/{modele_choisi}:generateContent?key={KEY}"
        prompt_combine = f"{SYSTEM}\n\nQUESTION DE L'UTILISATEUR GUINÉEN :\n{user_msg}"
        payload = {"contents": [{"parts": [{"text": prompt_combine}]}]}

        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200:
            txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"reply": txt.replace("\n", "<br>").replace("**", "<b>")})
        else:
            return jsonify({"reply": f"⚠️ Erreur {modele_choisi} ({r.status_code}) : {r.text[:150]}"})
    except Exception as e:
        return jsonify({"reply": f"⚠️ Erreur technique : {str(e)[:150]}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
