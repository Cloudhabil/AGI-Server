#!/usr/bin/env python3
"""
BOA Fluid Dynamics - Main Entry Point
Brahim Onion Agent for CFD & Navier-Stokes Simulation
"""

from flask import Flask, request, jsonify
from src.boa_cfd import FluidDynamicsAPI

app = Flask(__name__)
api = FluidDynamicsAPI()

@app.route('/cavity', methods=['GET', 'POST'])
def cavity():
    params = request.args.to_dict() if request.method == 'GET' else request.json or {}
    for key in ['velocity', 'density', 'viscosity', 'length']:
        if key in params:
            params[key] = float(params[key])
    return jsonify(api.handle_request('/cavity', params))

@app.route('/drag', methods=['GET', 'POST'])
def drag():
    params = request.args.to_dict() if request.method == 'GET' else request.json or {}
    for key in ['velocity', 'density', 'viscosity', 'length']:
        if key in params:
            params[key] = float(params[key])
    return jsonify(api.handle_request('/drag', params))

@app.route('/reynolds', methods=['GET', 'POST'])
def reynolds():
    params = request.args.to_dict() if request.method == 'GET' else request.json or {}
    for key in ['velocity', 'density', 'viscosity', 'length']:
        if key in params:
            params[key] = float(params[key])
    return jsonify(api.handle_request('/reynolds', params))

@app.route('/health', methods=['GET'])
def health():
    return jsonify(api.handle_request('/health', {}))

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "sdk": "BOA Fluid Dynamics",
        "version": "1.0.0",
        "endpoints": ["/cavity", "/drag", "/reynolds", "/health"],
        "security": "Brahim Onion Layer",
        "millennium_problem": "Navier-Stokes"
    })

if __name__ == '__main__':
    print("BOA Fluid Dynamics SDK - Starting server...")
    app.run(host='0.0.0.0', port=5003, debug=False)
