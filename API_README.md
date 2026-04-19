# OmniVoice FastAPI

API REST para conversão de texto em fala usando o modelo OmniVoice.

## 🚀 Instalação

### 1. Instalar dependências

```bash
pip install fastapi uvicorn[standard] python-multipart pyngrok python-dotenv
```

Ou reinstalar o projeto com as novas dependências:

```bash
pip install -e .
```

### 2. Configurar arquivo .env

Crie um arquivo `.env` na raiz do projeto com as configurações:

```bash
python create_env.py
```

Ou copie manualmente:

```bash
cp .env.example .env
```

O arquivo `.env` contém:

```env
# Porta do servidor API (padrão: 8001)
API_PORT=8001

# Host do servidor
API_HOST=0.0.0.0

# Modelo a ser carregado
MODEL_PATH=k2-fsa/OmniVoice

# Dispositivo (deixe vazio para auto-detecção)
DEVICE=

# Criar link público via ngrok
SHARE=false
```

**Nota:** O script `start_api.bat` cria automaticamente o `.env` se não existir.

## 📡 Iniciar a API

### Opção 1: Script Batch (Windows)

Clique duas vezes em `start_api.bat` ou execute:

```bash
start_api.bat
```

### Opção 2: Linha de comando

```bash
python -m omnivoice.api
```

A API usará as configurações do arquivo `.env` automaticamente.

### Opção 3: Comando instalado

```bash
omnivoice-api
```

### Opção 4: Sobrescrever configurações do .env

Você pode sobrescrever as configurações do `.env` via linha de comando:

```bash
python -m omnivoice.api --port 8002 --share
```

## 🌐 Parâmetros de Inicialização

Todos os parâmetros são opcionais e sobrescrevem as configurações do `.env`:

- `--model`: Caminho do modelo ou ID do HuggingFace (padrão do .env: `k2-fsa/OmniVoice`)
- `--device`: Dispositivo (cuda/cpu/mps) - auto-detectado se não especificado
- `--host`: Host do servidor (padrão do .env: `0.0.0.0`)
- `--port`: Porta do servidor (padrão do .env: `8001`)
- `--share`: Criar link público via ngrok (padrão do .env: `false`)

## 📚 Documentação da API

Após iniciar o servidor, acesse:

- **Documentação interativa (Swagger)**: http://localhost:8001/docs
- **Documentação alternativa (ReDoc)**: http://localhost:8001/redoc

**Nota:** Se você alterou a porta no `.env`, use a porta configurada.

## 🎯 Endpoints

### 1. Health Check

```http
GET /health
```

Verifica se a API está funcionando e se o modelo está carregado.

### 2. Conversão de Voz

```http
POST /api/v1/voice-conversion
```

#### Parâmetros (Form Data):

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `text` | string | ✅ Sim | Texto para sintetizar |
| `language` | string | ❌ Não | Idioma (ex: "Portuguese", "English", "Auto") |
| `ref_audio` | file | ❌ Não | Arquivo de áudio de referência para clonagem de voz |
| `ref_text` | string | ❌ Não | Transcrição do áudio de referência |
| `num_step` | integer | ❌ Não | Número de passos de inferência (4-64, padrão: 32) |
| `guidance_scale` | float | ❌ Não | Escala de orientação (0.0-4.0, padrão: 2.0) |
| `denoise` | boolean | ❌ Não | Aplicar redução de ruído (padrão: true) |
| `speed` | float | ❌ Não | Velocidade da fala (0.5-1.5, padrão: 1.0) |
| `duration` | float | ❌ Não | Duração fixa em segundos |

#### Resposta:

```json
{
  "audio_base64": "UklGRiQAAABXQVZFZm10...",
  "sample_rate": 24000,
  "message": "Audio generated successfully"
}
```

## 💡 Exemplos de Uso

### Exemplo 1: Python com requests

```python
import requests
import base64

url = "http://localhost:8001/api/v1/voice-conversion"

data = {
    "text": "Olá, este é um teste de conversão de voz.",
    "language": "Portuguese",
    "num_step": 32,
    "guidance_scale": 2.0,
    "denoise": True,
    "speed": 1.0
}

response = requests.post(url, data=data)
result = response.json()

audio_bytes = base64.b64decode(result["audio_base64"])
with open("output.wav", "wb") as f:
    f.write(audio_bytes)

print(f"Áudio salvo! Sample rate: {result['sample_rate']}")
```

### Exemplo 2: Com clonagem de voz

```python
import requests
import base64

url = "http://localhost:8001/api/v1/voice-conversion"

data = {
    "text": "Este áudio terá a voz do arquivo de referência.",
    "language": "Portuguese",
}

files = {
    "ref_audio": open("reference_voice.wav", "rb")
}

response = requests.post(url, data=data, files=files)
result = response.json()

audio_bytes = base64.b64decode(result["audio_base64"])
with open("cloned_output.wav", "wb") as f:
    f.write(audio_bytes)
```

### Exemplo 3: cURL

```bash
curl -X POST "http://localhost:8001/api/v1/voice-conversion" \
  -F "text=Olá, como você está?" \
  -F "language=Portuguese" \
  -F "num_step=32" \
  -F "guidance_scale=2.0"
```

### Exemplo 4: JavaScript (Fetch API)

```javascript
const formData = new FormData();
formData.append('text', 'Hello, this is a test.');
formData.append('language', 'English');
formData.append('num_step', '32');

fetch('http://localhost:8001/api/v1/voice-conversion', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  const audioBytes = atob(data.audio_base64);
  const audioArray = new Uint8Array(audioBytes.length);
  for (let i = 0; i < audioBytes.length; i++) {
    audioArray[i] = audioBytes.charCodeAt(i);
  }
  const blob = new Blob([audioArray], { type: 'audio/wav' });
  const url = URL.createObjectURL(blob);
  
  const audio = new Audio(url);
  audio.play();
});
```

## 🌍 Link Público

Para criar um link público acessível de qualquer lugar:

```bash
python -m omnivoice.api --model k2-fsa/OmniVoice --port 8000 --share
```

Isso criará um link ngrok que você pode compartilhar. Exemplo:
```
Public URL: https://abc123.ngrok.io
API Docs: https://abc123.ngrok.io/docs
```

## 🔧 Solução de Problemas

### Erro: "pyngrok not installed"

```bash
pip install pyngrok
```

### Erro: "Model not loaded"

Verifique se o modelo foi carregado corretamente. Aguarde a mensagem:
```
Model loaded successfully.
```

### Porta já em uso

Altere a porta:
```bash
python -m omnivoice.api --port 8001 --share
```

## 📝 Notas

- O primeiro request pode demorar mais devido ao carregamento do modelo
- Áudios de referência recomendados: 3-10 segundos
- Formatos de áudio suportados: WAV, MP3, FLAC, etc.
- O áudio retornado está em formato WAV codificado em base64

## 🎨 Idiomas Suportados

A API suporta mais de 600 idiomas. Alguns exemplos:

- Portuguese / Português
- English / Inglês
- Spanish / Espanhol
- French / Francês
- German / Alemão
- Chinese / 中文
- Japanese / 日本語
- Korean / 한국어
- Auto (detecção automática)

Para lista completa, consulte a documentação do OmniVoice.
