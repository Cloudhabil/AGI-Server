$ErrorActionPreference = 'Stop'

$env:OLLAMA_MODELS = 'C:\Users\usuario\Business\CLI_A1_GHR\CLI-main\models'
$env:OLLAMA_HOST = '127.0.0.1:11435'

& 'C:\Users\usuario\AppData\Local\Programs\Ollama\ollama.exe' serve
