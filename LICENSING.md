# Third-Party Component Licensing

This document provides licensing information for third-party components that may be used locally but are **not included** in this repository.

## Components NOT in Repository

The following components are excluded from version control (via `.gitignore`) due to size and licensing considerations. Users must obtain them independently.

### 1. NVIDIA TensorRT-LLM Runtime

| Component | License | Source |
|-----------|---------|--------|
| `tensorrt_llm-0.9.0-cp310-cp310-win_amd64.whl` | [NVIDIA License](https://docs.nvidia.com/deeplearning/tensorrt/sla/index.html) | [NVIDIA NGC](https://catalog.ngc.nvidia.com/) |
| TensorRT Libraries | NVIDIA Software License Agreement | Bundled with CUDA Toolkit |

**Restrictions:**
- Redistribution prohibited without NVIDIA authorization
- Commercial use requires compliance with NVIDIA EULA
- Export control restrictions may apply

### 2. Mistral 7B INT4 AWQ Weights

| Component | License | Source |
|-----------|---------|--------|
| `rank0.safetensors` (~4GB) | Apache 2.0 | [Mistral AI](https://huggingface.co/mistralai) |
| Tokenizer files | Apache 2.0 | [Mistral AI](https://huggingface.co/mistralai) |

**Note:** While the model weights are Apache 2.0 licensed, the quantized AWQ format may have additional considerations from the quantization toolkit used.

### 3. ChatRTX Reference Implementation

| Component | License | Source |
|-----------|---------|--------|
| `trt-llm-rag-windows-ChatRTX_0.4.0` | MIT | [NVIDIA ChatRTX](https://github.com/NVIDIA/ChatRTX) |

**Usage:** Reference code only. Not executed directly.

---

## Local Setup Instructions

To obtain these components legally:

```bash
# 1. TensorRT-LLM (requires NVIDIA Developer account)
pip install tensorrt_llm --extra-index-url https://pypi.nvidia.com

# 2. Mistral Weights (Apache 2.0)
huggingface-cli download mistralai/Mistral-7B-Instruct-v0.2

# 3. AWQ Quantization (optional)
# See: https://github.com/mit-han-lab/llm-awq
```

---

## Compliance Checklist

Before deploying systems using these components:

- [ ] Verify NVIDIA EULA compliance for TensorRT usage
- [ ] Ensure export control compliance (EAR/ITAR if applicable)
- [ ] Review Mistral AI acceptable use policy
- [ ] Document hardware requirements (NVIDIA GPU with CUDA support)

---

## Contact

For licensing questions regarding this project's use of third-party components, consult the original license holders:

- NVIDIA: https://www.nvidia.com/en-us/about-nvidia/legal-info/
- Mistral AI: https://mistral.ai/terms/
- Hugging Face: https://huggingface.co/terms-of-service

---

*This document does not constitute legal advice. Consult with legal counsel for compliance matters.*
