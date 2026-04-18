import os
import json
import urllib.request
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({'status': 'ok', 'service': 'action-plan-builder'})

@app.route('/')
def index():
    with open(os.path.join(os.path.dirname(__file__), 'index.html'), 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'text/html'}

@app.route('/api/plan', methods=['POST'])
def generate_plan():
    data = request.json
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({'error': 'prompt required'}), 400

    api_key = os.getenv('MINIMAX_API_KEY')
    if not api_key:
        return jsonify({'error': 'API key not configured'}), 503

    try:
        url = 'https://api.minimax.io/v1/chat/completions'
        payload = json.dumps({
            'model': 'MiniMax-M2.7',
            'max_tokens': 1200,
            'messages': [{'role': 'user', 'content': prompt}]
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key
        })
        with urllib.request.urlopen(req, timeout=60) as r:
            result = json.loads(r.read().decode())
            raw = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            return jsonify({'raw': raw})
    except urllib.error.HTTPError as e:
        return jsonify({'error': f'HTTP {e.code}: {e.read().decode()}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
