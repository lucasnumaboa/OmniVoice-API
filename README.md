# OmniVoice-API

<p align="center">
  <img width="160" height="160" alt="OmniVoice" src="https://zhu-han.github.io/omnivoice/pics/omnivoice.jpg" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" alt="FastAPI">
  &nbsp;
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python" alt="Python">
  &nbsp;
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?logo=docker" alt="Docker">
  &nbsp;
  <img src="https://img.shields.io/badge/600%2B_Languages-TTS-green" alt="Languages">
  &nbsp;
  <a href="https://github.com/k2-fsa/OmniVoice"><img src="https://img.shields.io/badge/Base-OmniVoice-FFD21E" alt="Base: OmniVoice"></a>
</p>

**OmniVoice-API** é uma API REST construída sobre o modelo [OmniVoice](https://github.com/k2-fsa/OmniVoice) — um modelo TTS multilingual zero-shot de última geração que suporta mais de 600 idiomas com clonagem de voz e síntese em tempo real.

> **Base:** Este projeto usa o [k2-fsa/OmniVoice](https://github.com/k2-fsa/OmniVoice) como modelo de inferência, adicionando uma camada de API REST via FastAPI com suporte a voz padrão, Docker e integração facilitada.

---

## Índice

- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Iniciando a API](#iniciando-a-api)
- [Docker](#docker)
- [Endpoints](#endpoints)
- [Exemplos de Chamadas](#exemplos-de-chamadas)
- [Processamento em Batch](#processamento-em-batch)
- [Parâmetros](#parâmetros)
- [Idiomas Suportados](#idiomas-suportados)
- [Solução de Problemas](#solução-de-problemas)
- [Créditos](#créditos)

---

## Funcionalidades

- **REST API com FastAPI** — documentação Swagger automática em `/docs`
- **Clonagem de voz** — envie um áudio de referência e replique qualquer voz
- **Voz padrão automática** — usa `voice.wav` quando nenhuma referência é enviada
- **600+ idiomas** — detecção automática ou seleção manual
- **Processamento em batch** — endpoint `/batch` para múltiplos textos numa única chamada, maximizando o throughput da GPU
- **Ngrok integrado** — exponha a API publicamente com `--share`
- **CORS habilitado** — pronto para integração com front-ends
- **Docker ready** — imagem pronta para CPU e GPU (CUDA)

---

## Instalação

> Recomenda-se um ambiente virtual (`venv`, `conda`, etc.)

### Opção 1 — pip

**1. Instalar PyTorch**

<details>
<summary>NVIDIA GPU (CUDA)</summary>

```bash
pip install torch==2.8.0+cu128 torchaudio==2.8.0+cu128 --extra-index-url https://download.pytorch.org/whl/cu128
```

</details>

<details>
<summary>CPU / Apple Silicon</summary>

```bash
pip install torch==2.8.0 torchaudio==2.8.0
```

</details>

**2. Instalar o projeto**

```bash
git clone https://github.com/lucasnumaboa/OmniVoice-API.git
cd OmniVoice-API
pip install -e .
```

### Opção 2 — uv

```bash
git clone https://github.com/lucasnumaboa/OmniVoice-API.git
cd OmniVoice-API
uv sync
```

---

## Configuração

### Arquivo `.env`

Crie o arquivo de configuração automaticamente:

```bash
python create_env.py
```

Ou copie o exemplo e edite manualmente:

```bash
cp .env.example .env
```

Conteúdo do `.env`:

```env
# Porta do servidor API (padrão: 8001)
API_PORT=8001

# Host do servidor (0.0.0.0 = acesso externo, 127.0.0.1 = somente local)
API_HOST=0.0.0.0

# Modelo a ser carregado (HuggingFace repo ou caminho local)
MODEL_PATH=k2-fsa/OmniVoice

# Dispositivo: cuda, cpu, mps — deixe vazio para auto-detecção
DEVICE=

# Criar link público via ngrok (true/false)
SHARE=false
```

### Voz padrão (`voice.wav`)

Coloque um arquivo `voice.wav` na raiz do projeto. Quando nenhum `ref_audio` for enviado na requisição, a API usará esse arquivo automaticamente como voz de referência.

---

## Iniciando a API

### Windows (`.bat`)

```bash
start_api.bat
```

### Linha de comando

```bash
python -m omnivoice.api
```

### Comando instalado

```bash
omnivoice-api
```

### Sobrescrevendo configurações do `.env`

```bash
python -m omnivoice.api --port 8002 --host 0.0.0.0 --share
```

**Parâmetros disponíveis:**

| Parâmetro | Descrição | Padrão (do `.env`) |
|-----------|-----------|-------------------|
| `--model` | Caminho do modelo ou ID HuggingFace | `k2-fsa/OmniVoice` |
| `--device` | Dispositivo (`cuda`/`cpu`/`mps`) | auto-detecção |
| `--host` | Host do servidor | `0.0.0.0` |
| `--port` | Porta do servidor | `8001` |
| `--share` | Criar link público via ngrok | `false` |

Após iniciar, acesse:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

---

## Docker

### Build da imagem

```bash
docker build -t omnivoice-api .
```

### Executar (CPU)

```bash
docker run -p 8001:8001 \
  -e MODEL_PATH=k2-fsa/OmniVoice \
  -e DEVICE=cpu \
  -v $(pwd)/voice.wav:/app/voice.wav \
  omnivoice-api
```

### Executar (GPU — requer nvidia-container-toolkit)

```bash
docker run --gpus all -p 8001:8001 \
  -e MODEL_PATH=k2-fsa/OmniVoice \
  -e DEVICE=cuda \
  -v $(pwd)/voice.wav:/app/voice.wav \
  omnivoice-api
```

### Docker Compose

```bash
docker compose up
```

---

## Endpoints

### `GET /`

Retorna informações básicas da API.

```json
{
  "message": "OmniVoice API is running",
  "docs": "/docs",
  "endpoints": {
    "voice_conversion": "/api/v1/voice-conversion",
    "health": "/health"
  }
}
```

---

### `GET /health`

Verifica se a API está online e se o modelo está carregado.

```json
{
  "status": "healthy",
  "model_loaded": true
}
```

---

### `POST /api/v1/voice-conversion`

Converte texto em fala.

**Content-Type:** `multipart/form-data`

#### Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|:-----------:|-----------|
| `text` | `string` | ✅ | Texto a sintetizar |
| `language` | `string` | ❌ | Idioma (ex: `"Portuguese"`, `"English"`, `"Auto"`) |
| `ref_audio` | `file` | ❌ | Áudio de referência para clonagem de voz (usa `voice.wav` se omitido) |
| `ref_text` | `string` | ❌ | Transcrição do áudio de referência (auto-transcrito pelo Whisper se omitido) |
| `num_step` | `integer` | ❌ | Passos de inferência (4–64, padrão: `32`) |
| `guidance_scale` | `float` | ❌ | Escala de orientação (0.0–4.0, padrão: `2.0`) |
| `denoise` | `boolean` | ❌ | Aplicar redução de ruído (padrão: `true`) |
| `speed` | `float` | ❌ | Velocidade da fala (0.5–1.5, padrão: `1.0`) |
| `duration` | `float` | ❌ | Duração fixa em segundos (sobrescreve `speed`) |

#### Resposta

```json
{
  "audio_base64": "UklGRiQAAABXQVZFZm10...",
  "sample_rate": 24000,
  "message": "Audio generated successfully"
}
```

O campo `audio_base64` é um arquivo WAV codificado em Base64.

---

### `POST /api/v1/voice-conversion/batch`

Converte múltiplos textos em fala numa única chamada, processando-os em lotes na GPU para máximo desempenho.

**Content-Type:** `multipart/form-data`

#### Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|:-----------:|-----------|
| `items` | `string` (JSON) | ✅ | Array JSON de objetos `{text, language?, speed?, duration?}` |
| `batch_size` | `integer` | ❌ | Número de itens por chamada de GPU (padrão: `4`) |
| `ref_audio` | `file` | ❌ | Áudio de referência compartilhado por todos os itens (usa `voice.wav` se omitido) |
| `ref_text` | `string` | ❌ | Transcrição do áudio de referência (auto-transcrito se omitido) |
| `num_step` | `integer` | ❌ | Passos de inferência compartilhados (padrão: `32`) |
| `guidance_scale` | `float` | ❌ | Escala de orientação compartilhada (padrão: `2.0`) |
| `denoise` | `boolean` | ❌ | Redução de ruído compartilhada (padrão: `true`) |

#### Formato do campo `items`

```json
[
  {"text": "Olá, como você está?", "language": "Portuguese"},
  {"text": "Hello, how are you?", "language": "English", "speed": 1.2},
  {"text": "Bonjour le monde.", "language": "French", "duration": 3.5}
]
```

#### Resposta

```json
{
  "results": [
    {"audio_base64": "UklGRiQ...", "sample_rate": 24000, "message": "Audio generated successfully"},
    {"audio_base64": "UklGRiQ...", "sample_rate": 24000, "message": "Audio generated successfully"}
  ],
  "total": 2,
  "batch_size": 4,
  "message": "Batch completed: 2 items processed"
}
```

Os resultados são retornados **na mesma ordem** dos itens de entrada.

---

## Exemplos de Chamadas

### Python — `requests`

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

### Python — com clonagem de voz

```python
import requests
import base64

url = "http://localhost:8001/api/v1/voice-conversion"

data = {
    "text": "Este áudio terá a voz do arquivo de referência.",
    "language": "Portuguese",
}

files = {
    "ref_audio": open("minha_voz.wav", "rb")
}

response = requests.post(url, data=data, files=files)
result = response.json()

audio_bytes = base64.b64decode(result["audio_base64"])
with open("cloned_output.wav", "wb") as f:
    f.write(audio_bytes)
```

### cURL

```bash
# Síntese simples (usa voice.wav como referência)
curl -X POST "http://localhost:8001/api/v1/voice-conversion" \
  -F "text=Olá, como você está?" \
  -F "language=Portuguese" \
  -F "num_step=32" \
  -F "guidance_scale=2.0"

# Com clonagem de voz
curl -X POST "http://localhost:8001/api/v1/voice-conversion" \
  -F "text=Este áudio usa a minha voz." \
  -F "language=Portuguese" \
  -F "ref_audio=@minha_voz.wav"
```

### JavaScript — Fetch API

```javascript
const formData = new FormData();
formData.append('text', 'Hello, this is a test.');
formData.append('language', 'English');
formData.append('num_step', '32');

const response = await fetch('http://localhost:8001/api/v1/voice-conversion', {
  method: 'POST',
  body: formData
});

const data = await response.json();

const audioBytes = atob(data.audio_base64);
const audioArray = new Uint8Array(audioBytes.length);
for (let i = 0; i < audioBytes.length; i++) {
  audioArray[i] = audioBytes.charCodeAt(i);
}

const blob = new Blob([audioArray], { type: 'audio/wav' });
const audio = new Audio(URL.createObjectURL(blob));
audio.play();
```

### Health Check

```bash
curl http://localhost:8001/health
```

---

## Processamento em Batch

O endpoint `/batch` envia múltiplos textos para o modelo de uma só vez, eliminando o aviso:

> *You seem to be using the pipelines sequentially on GPU. In order to maximize efficiency please use a dataset*

O parâmetro `batch_size` controla quantos itens são processados **por chamada de GPU**. Valores maiores aproveitam mais a paralelização da GPU mas consomem mais VRAM.

### Python — `requests`

```python
import requests
import base64
import json

url = "http://localhost:8001/api/v1/voice-conversion/batch"

items = [
    {"text": "Olá, este é o primeiro áudio.", "language": "Portuguese"},
    {"text": "Hello, this is the second audio.", "language": "English"},
    {"text": "Hola, este es el tercer audio.", "language": "Spanish"},
    {"text": "Bonjour, c'est le quatrième audio.", "language": "French"},
]

data = {
    "items": json.dumps(items),
    "batch_size": 4,
    "num_step": 32,
    "guidance_scale": 2.0,
    "denoise": True,
}

response = requests.post(url, data=data)
result = response.json()

for i, item_result in enumerate(result["results"]):
    audio_bytes = base64.b64decode(item_result["audio_base64"])
    with open(f"output_{i}.wav", "wb") as f:
        f.write(audio_bytes)

print(f'Processados: {result["total"]} áudios')
```

### Python — batch com clonagem de voz

```python
import requests
import base64
import json

url = "http://localhost:8001/api/v1/voice-conversion/batch"

items = [
    {"text": "Primeiro texto a sintetizar."},
    {"text": "Segundo texto a sintetizar."},
    {"text": "Terceiro texto.", "speed": 0.9},
]

data = {
    "items": json.dumps(items),
    "batch_size": 4,
}

files = {
    "ref_audio": open("minha_voz.wav", "rb")
}

response = requests.post(url, data=data, files=files)
result = response.json()

for i, item_result in enumerate(result["results"]):
    audio_bytes = base64.b64decode(item_result["audio_base64"])
    with open(f"batch_output_{i}.wav", "wb") as f:
        f.write(audio_bytes)
```

### cURL

```bash
curl -X POST "http://localhost:8001/api/v1/voice-conversion/batch" \
  -F 'items=[{"text":"Primeiro texto","language":"Portuguese"},{"text":"Second text","language":"English"}]' \
  -F "batch_size=4" \
  -F "num_step=32"
```

### Escolhendo o `batch_size` ideal

| VRAM disponível | `batch_size` recomendado |
|-----------------|-------------------------|
| 4 GB | 2 |
| 8 GB | 4 |
| 16 GB | 8 |
| 24 GB+ | 16+ |

---

## Parâmetros

| Parâmetro | Intervalo | Padrão | Efeito |
|-----------|-----------|--------|--------|
| `num_step` | 4 – 64 | 32 | Qualidade vs velocidade (mais passos = melhor qualidade) |
| `guidance_scale` | 0.0 – 4.0 | 2.0 | Aderência ao texto (valores maiores = mais fiel) |
| `speed` | 0.5 – 1.5 | 1.0 | Velocidade da fala |
| `duration` | > 0 (segundos) | — | Duração fixa (sobrescreve `speed`) |
| `denoise` | `true`/`false` | `true` | Redução de ruído no áudio |

---

## Idiomas Suportados

A API suporta **600+ idiomas**. Exemplos:

| Idioma | Valor do parâmetro |
|--------|-------------------|
| Português | `Portuguese` |
| Inglês | `English` |
| Espanhol | `Spanish` |
| Francês | `French` |
| Alemão | `German` |
| Chinês | `Chinese` |
| Japonês | `Japanese` |
| Coreano | `Korean` |
| Detecção automática | `Auto` |

Para a lista completa, consulte [docs/languages.md](docs/languages.md).

---

## Solução de Problemas

**`pyngrok not installed`**
```bash
pip install pyngrok
```

**`Model not loaded` (503)**

Aguarde a mensagem `Model loaded successfully.` no log antes de fazer requisições.

**Porta já em uso**
```bash
python -m omnivoice.api --port 8002
```

**Problema ao baixar o modelo do HuggingFace**
```bash
export HF_ENDPOINT="https://hf-mirror.com"
python -m omnivoice.api
```

**Primeira requisição lenta**

Normal — o modelo é carregado na primeira inferência. As seguintes serão mais rápidas.

**Aviso `pipelines sequentially on GPU`**

Use o endpoint `/api/v1/voice-conversion/batch` em vez de fazer múltiplas chamadas ao `/api/v1/voice-conversion`. O endpoint batch passa uma lista de textos diretamente ao modelo, eliminando o processamento sequencial.

---

## Créditos

Este projeto é baseado no **[OmniVoice](https://github.com/k2-fsa/OmniVoice)**, desenvolvido pelo time [k2-fsa](https://github.com/k2-fsa).

```bibtex
@article{zhu2026omnivoice,
  title={OmniVoice: Towards Omnilingual Zero-Shot Text-to-Speech with Diffusion Language Models},
  author={Zhu, Han and Ye, Lingxuan and Kang, Wei and Yao, Zengwei and Guo, Liyong and Kuang, Fangjun and Han, Zhifeng and Zhuang, Weiji and Lin, Long and Povey, Daniel},
  journal={arXiv preprint arXiv:2604.00688},
  year={2026}
}
```

---

## Licença

Apache 2.0 — veja [LICENSE](LICENSE).
