from flask import Flask, request, jsonify
from openai import OpenAI
import time

app = Flask(__name__)
client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")

@app.route('/chat', methods=['POST'])
def chat():
    start = time.time()
    try:
        resp = client.chat.completions.create(
            model="/root/models/Qwen2.5-7B-Instruct",
            messages=request.json.get("messages", []),
            temperature=request.json.get("temperature", 0.7),
            max_tokens=request.json.get("max_tokens", 512)
        )
        return jsonify({
            "reply": resp.choices[0].message.content,
            "latency": round(time.time() - start, 3),
            "prompt_tokens": resp.usage.prompt_tokens,
            "completion_tokens": resp.usage.completion_tokens,
            "total_tokens": resp.usage.total_tokens
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "model": "Qwen2.5-7B-Instruct",
        "gpu": "RTX 3090",
        "framework": "vLLM"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
