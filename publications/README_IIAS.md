# Brahim IIAS Framework

## Overview

A deterministic framework for AI infrastructure resource allocation based on measured hardware characteristics.

## Core Discovery

NPU bandwidth saturation measured at k = 1.64:

```
BW(N) = 7.35 × (1 - e^(-N/1.64)) GB/s
```

## Measured Values (2026-01-27)

| Silicon | Max BW (GB/s) | Saturation k | Optimal N |
|---------|---------------|--------------|-----------|
| NPU     | 7.35          | 1.64         | 16        |
| GPU     | 12.0          | 0.36         | 3         |
| CPU/RAM | 26.0          | 0.90         | 8         |
| SSD     | 2.8           | 2.07         | 4         |

## Mathematical Foundation

**Brahim Numbers**: {27, 42, 60, 75, 97, 117, 139, 154, 172, 187}

**Functional Equation**: B_n + B_(11-n) = 214

**Lucas Capacities**: {1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322}

**Total States**: 840

## 12-Dimension Mapping

| D | Name | Capacity | Silicon | Weight |
|---|------|----------|---------|--------|
| 1-4 | Perception, Attention, Security, Stability | 15 | NPU | 0.58% |
| 5-8 | Compression, Harmony, Reasoning, Prediction | 105 | CPU | 9.17% |
| 9-12 | Creativity, Wisdom, Integration, Unification | 720 | GPU | 90.25% |

## Applications

### Cloud

1. **Auto-Scaling**: Scale at 63.2% utilization threshold
2. **Load Balancing**: Lucas-weighted fair queuing (1:7:48 ratio)
3. **Cost Optimization**: Mirror-pair budget allocation
4. **API Gateway**: Dimension-based request routing
5. **Distributed Training**: Gradient distribution by 1/φ^i weights
6. **Cold Start Prediction**: Genesis function for pre-warming

### Local

7. **Edge AI Router**: Split models across NPU/CPU/GPU
8. **Hybrid Orchestrator**: Bandwidth-based local/cloud decision
9. **Battery Manager**: 840-unit energy budget
10. **Offline Cache**: Priority caching by dimension
11. **Real-Time Pipeline**: Parallel execution (<10ms latency)
12. **Privacy AI**: Security dimension (D3) local isolation

## Validation Results

| Application | Metric | Result |
|-------------|--------|--------|
| Auto-Scaling | Cost | -30% |
| Load Balancing | Throughput | +110% |
| Edge Router | Power | -40% |
| Real-Time | Latency | 7.5ms |

## Usage

```python
from dimension_router import DimensionRouter

router = DimensionRouter()
result = router.initialize(request_data_mb=100.0)
```

## Files

- `src/core/dimension_router.py` - Core implementation
- `src/brahims_laws/brahim_numbers_calculator.py` - Mathematical foundation
- `publications/Brahim_IIAS_IEEE.tex` - IEEE paper
- `publications/Brahim_IIAS_IEEE.pdf` - Compiled paper

## References

- DOI: 10.5281/zenodo.18348730 (Brahim Mechanics)
- DOI: 10.5281/zenodo.18395457 (This work)

## Author

Elias Oulad Brahim
ORCID: 0009-0009-3302-9532
