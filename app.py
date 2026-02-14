from flask import Flask, render_template, request, jsonify
import requests
import socket
import os

app = Flask(__name__)

# =========================
# CONFIG
# =========================
OPENAI_API_KEY = "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"

# =========================
# OSINT / RECON (SAFE)
# =========================
def recon(target):
    data = {}

    # DNS lookup
    try:
        data["ip"] = socket.gethostbyname(target)
    except:
        data["ip"] = "Not resolvable"

    # HTTP headers
    try:
        r = requests.get("http://" + target, timeout=5)
        data["headers"] = dict(r.headers)
    except:
        data["headers"] = "Unavailable"

    return data

# =========================
# AI BRAIN (like ChatGPT)
# =========================
def ask_ai(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are Pentest GPT. "
        "You act like ChatGPT. "
        "You provide ethical cybersecurity analysis, OSINT, and recon results. "
        "You NEVER give illegal hacking or exploitation steps. "
        "You write like a professional penetration tester."
    )

    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post(url, headers=headers, json=payload)
    return r.json()["choices"][0]["message"]["content"]

# =========================
# ROUTES
# =========================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan():
    query = request.json["query"]

    # If user asks a normal question → just AI
    if "." not in query and " " in query:
        ai_reply = ask_ai(query)
        return jsonify({"result": ai_reply})

    # If looks like domain/IP → recon + AI report
    data = recon(query)

    ai_prompt = f"""
Target: {query}

OSINT Data:
{data}

Write a pentest-style recon report.
Include:
- Findings
- Risk level
- Recommendations
"""

    ai_reply = ask_ai(ai_prompt)
    return jsonify({"result": ai_reply})

app.run(debug=True)
