#!/usr/bin/env python3
"""
BOA Titan Explorer - Main Entry Point
Brahim Onion Agent for Planetary Science & Observation Analysis
"""

from flask import Flask, request, jsonify
from src.boa_titan import TitanExplorerAPI

app = Flask(__name__)
api = TitanExplorerAPI()

@app.route('/properties', methods=['GET'])
def properties():
    return jsonify(api.handle_request('/properties', {}))

@app.route('/methane', methods=['GET', 'POST'])
def methane():
    params = request.args.to_dict() if request.method == 'GET' else request.json or {}
    if 'latitude' in params:
        params['latitude'] = float(params['latitude'])
    return jsonify(api.handle_request('/methane', params))

@app.route('/mission', methods=['GET', 'POST'])
def mission():
    params = request.args.to_dict() if request.method == 'GET' else request.json or {}
    for key in ['latitude', 'longitude']:
        if key in params:
            params[key] = float(params[key])
    return jsonify(api.handle_request('/mission', params))

@app.route('/prebiotic', methods=['GET'])
def prebiotic():
    return jsonify(api.handle_request('/prebiotic', {}))

@app.route('/cryogenic', methods=['GET'])
def cryogenic():
    return jsonify(api.handle_request('/cryogenic', {}))

@app.route('/statistics', methods=['GET'])
def statistics():
    return jsonify(api.handle_request('/statistics', {}))

@app.route('/health', methods=['GET'])
def health():
    return jsonify(api.handle_request('/health', {}))

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "sdk": "BOA Titan Explorer",
        "version": "1.0.0",
        "endpoints": ["/properties", "/methane", "/mission", "/prebiotic", "/cryogenic", "/statistics", "/health"],
        "security": "Brahim Onion Layer",
        "data_source": "NASA PDS / SETI"
    })

if __name__ == '__main__':
    print("BOA Titan Explorer SDK - Starting server...")
    app.run(host='0.0.0.0', port=5004, debug=False)
