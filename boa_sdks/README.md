# BOA SDKs - Brahim Onion Agent Toolkits

Four specialized ML Agent SDKs wrapped in Brahim Onion security layer.

## SDKs

| SDK | Port | Domain | Applications |
|-----|------|--------|--------------|
| `boa-egyptian-fractions` | 5001 | Number Theory | Fair division, scheduling, secret splitting |
| `boa-sat-solver` | 5002 | P vs NP | Circuit verification, bug detection, AI planning |
| `boa-fluid-dynamics` | 5003 | Navier-Stokes | Aerodynamics, weather, blood flow, HVAC |
| `boa-titan-explorer` | 5004 | Planetary Science | Atmosphere modeling, mission planning, cryogenics |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run individual SDK
cd egyptian_fractions && python main.py

# Build all as executables
python build_all.py
```

## API Endpoints

### Egyptian Fractions (port 5001)
```
GET  /solve?n=5              # Find 4/n = 1/a + 1/b + 1/c
GET  /fair_division?total=100&n=5
POST /split_secret           # {"secret": "...", "n": 5}
GET  /health
```

### SAT Solver (port 5002)
```
POST /solve                  # {"cnf": "p cnf 3 2\n1 2 0\n..."}
POST /analyze
POST /verify_circuit
POST /find_bug
GET  /health
```

### Fluid Dynamics (port 5003)
```
GET  /reynolds?velocity=10&density=1.225&viscosity=1.81e-5&length=1
GET  /drag?velocity=30&shape=cylinder
GET  /cavity?velocity=1&viscosity=0.01
GET  /health
```

### Titan Explorer (port 5004)
```
GET  /properties
GET  /methane?latitude=75
GET  /mission?latitude=45&longitude=120
GET  /prebiotic
GET  /cryogenic
GET  /health
```

## Security

All SDKs use Brahim Onion Layer encryption:
- β = √5 - 2 = 0.2360679... (security constant)
- 3-layer SHA256 onion encoding
- Integrity verification on all data

## Build Executables

```bash
python build_all.py
```

Output in `dist/`:
- `boa-egyptian-fractions.exe`
- `boa-sat-solver.exe`
- `boa-fluid-dynamics.exe`
- `boa-titan-explorer.exe`

## Data Sources

| SDK | Research Data |
|-----|---------------|
| Egyptian Fractions | 66,738 hard case primes |
| SAT Solver | 3,000 SATLIB instances |
| Fluid Dynamics | 539 SU2 CFD cases |
| Titan Explorer | 187,261 NASA observations |

## License

Brahim Security License - See LICENSE.md
