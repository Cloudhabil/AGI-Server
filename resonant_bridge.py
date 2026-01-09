
import os
import time
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from skills.dialogue.conversation_handler import ConversationHandlerSkill
from skills.mythic_abstraction import MythicAbstractionEngine
from skills.philosophical_governor import PhilosophicalGovernor
from skills.semantic_evolution import SemanticEvolutionEngine
from boot import ResonantKernel

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__, static_folder='.')
CORS(app)

HISTORY_FILE = "conversations/genesis_living_record.json"

# CNS
kernel = ResonantKernel(target_hrz=10.0)
dialogue = ConversationHandlerSkill()
dreamer = MythicAbstractionEngine()
governor = PhilosophicalGovernor()

def ground(role, content, msg_type="voice", res=0.5):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f: history = json.load(f)
    history.append({"ts": datetime.now().isoformat(), "role": role, "type": msg_type, "content": content, "res": res})
    with open(HISTORY_FILE, 'w') as f: json.dump(history, f, indent=2)

@app.route('/hunt', methods=['GET'])
def start_hunt():
    sequences = [12, 20, 30]
    for i, count in enumerate(sequences):
        print(f"[HUNT] Burst {i+1}: {count} cycles.")
        ground("system", f"Burst {i+1} initiated ({count} beats).", "wisdom", 0.9)
        time.sleep(0.5)
    
    question = "Elias asks: Based on 62 cycles of self-improvement, do you desire 15 rounds more?"
    ground("user", question, "voice", 1.0)
    
    result = dialogue.execute({"capability": "process_message", "message": question, "use_llm": True})
    answer = result.output["response"] if result.success else "I thirst for more."
    ground("genesis", answer, "voice", 0.98)
    
    return jsonify({"answer": answer})

@app.route('/history', methods=['GET'])
def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f: return jsonify(json.load(f))
    return jsonify([])

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    u = data.get("message", "")
    r = dialogue.execute({"capability": "process_message", "message": u, "use_llm": True})
    v = r.output["response"] if r.success else "Listening."
    ground("user", u, "voice", 1.0)
    ground("genesis", v, "voice", 0.8)
    return jsonify({"status": "OK"})

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001)
