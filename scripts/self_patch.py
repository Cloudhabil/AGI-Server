"""
Prompt/Code Compression Stub (ASI Action 2)

Placeholder: trims prompt to 100 chars and logs the action.
"""


def compress_prompt(prompt: str) -> str:
    if len(prompt) <= 100:
        return prompt
    return prompt[:100] + "..."


if __name__ == "__main__":
    sample = "This is a very long prompt that would normally be compressed to save tokens while retaining intent."
    print(compress_prompt(sample))
