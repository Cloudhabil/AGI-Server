# H-Net and OpenVINO Integration

The system uses **H-Net** to maintain long-horizon context with dynamic chunking and hierarchical summaries. Chunking logic lives in `src/hnet/dynamic_chunker.py` and the indices are stored under `data/hier_mem/`.

OpenVINO accelerates embedding generation when enabled:

```python
from integrations.openvino_embedder import get_embeddings
vector = get_embeddings("sample text")
```

Embedding backend order:
1) NPU (OpenVINO)
2) Ollama embeddings
3) sentence-transformers (CPU)

Set `USE_OPENVINO=1` and `OPENVINO_EMBEDDING_MODEL` / `OPENVINO_TOKENIZER` to enable NPU inference.
