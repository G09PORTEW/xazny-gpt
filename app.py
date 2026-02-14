from flask import Flask, render_template, request, jsonify
import requests
import socket
import os

app = Flask(__name__)

# =========================
# CONFIG: PUT YOUR API KEY
# =========================
OPENAI_API_KEY = "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"

if OPENAI_API_KEY == "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":
    print("⚠️ WARNING: You must set your OpenAI API key!")

# =========================
# SAFE OSINT / RECON
# =========================
def recon(target):
    data = {}
    # DNS lookup
    try:
        data["ip"] = socket.gethostbyname(target)
    except Exception as e:
        data["ip"] = f"Not resolvable ({e})"

    # HTTP headers
    try:
        r = requests.get("http://" + target, timeout=5)
        data["headers"] = dict(r.headers)
    except Exception as e:
        data["headers"] = f"Unavailable ({e})"

    return data

# =========================
# AI BRAIN
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
        "model": "gpt-4.1-mini",  # or "gpt-3.5-turbo" if no GPT-4
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        result = r.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print("❌ OpenAI API request failed:", e)
        return "⚠️ AI request failed. Check your API key or network."
    except Exception as e:
        print("❌ Unexpected error:", e)
        return "⚠️ Unexpected error in AI response."

# =========================
# ROUTES
# =========================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan():
    query = request.json.get("query", "").strip()
    if not query:
        return jsonify({"result": "⚠️ Please enter a domain, IP, or question."})

    # Determine if normal question or domain/IP
    if "." not in query and " " in query:
        # Just AI question
        ai_reply = ask_ai(query)
        return jsonify({"result": ai_reply})

    # Otherwise, treat as target for recon
    data = recon(query)
    print("🔍 Recon data:", data)  # debug log

    ai_prompt = f"""
Target: {query}

OSINT / Recon Data:
{data}

Write a pentest-style report.
Include:
- Findings
- Risk level
- Recommendations
"""

    ai_reply = ask_ai(ai_prompt)
    print("🧠 AI reply:", ai_reply[:200])  # first 200 chars
    return jsonify({"result": ai_reply})

if __name__ == "__main__":
    print("🚀 Starting Pentest GPT...")
    app.run(debug=True)
