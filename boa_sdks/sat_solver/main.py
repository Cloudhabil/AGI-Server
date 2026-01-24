#!/usr/bin/env python3
"""
BOA SAT Solver - Main Entry Point
Brahim Onion Agent for Constraint Satisfaction & Verification
"""

from flask import Flask, request, jsonify
from src.boa_sat import SATSolverAPI

app = Flask(__name__)
api = SATSolverAPI()

@app.route('/solve', methods=['POST'])
def solve():
    params = request.json or {}
    return jsonify(api.handle_request('/solve', params))

@app.route('/analyze', methods=['POST'])
def analyze():
    params = request.json or {}
    return jsonify(api.handle_request('/analyze', params))

@app.route('/verify_circuit', methods=['POST'])
def verify_circuit():
    params = request.json or {}
    return jsonify(api.handle_request('/verify_circuit', params))

@app.route('/find_bug', methods=['POST'])
def find_bug():
    params = request.json or {}
    return jsonify(api.handle_request('/find_bug', params))

@app.route('/health', methods=['GET'])
def health():
    return jsonify(api.handle_request('/health', {}))

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "sdk": "BOA SAT Solver",
        "version": "1.0.0",
        "endpoints": ["/solve", "/analyze", "/verify_circuit", "/find_bug", "/health"],
        "security": "Brahim Onion Layer",
        "phase_transition": 4.26
    })

if __name__ == '__main__':
    print("BOA SAT Solver SDK - Starting server...")
    app.run(host='0.0.0.0', port=5002, debug=False)
