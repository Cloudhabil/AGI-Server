#!/usr/bin/env python3
"""
BOA Egyptian Fractions - Main Entry Point
Brahim Onion Agent for Fair Division & Resource Optimization
"""

from flask import Flask, request, jsonify
from src.boa_egyptian import EgyptianFractionsAPI

app = Flask(__name__)
api = EgyptianFractionsAPI()

@app.route('/solve', methods=['GET', 'POST'])
def solve():
    params = request.args.to_dict() if request.method == 'GET' else request.json or {}
    params['n'] = int(params.get('n', 5))
    return jsonify(api.handle_request('/solve', params))

@app.route('/fair_division', methods=['GET', 'POST'])
def fair_division():
    params = request.args.to_dict() if request.method == 'GET' else request.json or {}
    params['total'] = float(params.get('total', 100))
    params['n'] = int(params.get('n', 5))
    return jsonify(api.handle_request('/fair_division', params))

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    params = request.args.to_dict() if request.method == 'GET' else request.json or {}
    params['duration'] = int(params.get('duration', 60))
    params['n'] = int(params.get('n', 5))
    return jsonify(api.handle_request('/schedule', params))

@app.route('/split_secret', methods=['POST'])
def split_secret():
    params = request.json or {}
    return jsonify(api.handle_request('/split_secret', params))

@app.route('/health', methods=['GET'])
def health():
    return jsonify(api.handle_request('/health', {}))

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "sdk": "BOA Egyptian Fractions",
        "version": "1.0.0",
        "endpoints": ["/solve", "/fair_division", "/schedule", "/split_secret", "/health"],
        "security": "Brahim Onion Layer"
    })

if __name__ == '__main__':
    print("BOA Egyptian Fractions SDK - Starting server...")
    app.run(host='0.0.0.0', port=5001, debug=False)
