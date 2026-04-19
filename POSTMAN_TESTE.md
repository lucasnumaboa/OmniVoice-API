# Teste Postman - OmniVoice API

**IMPORTANTE:** Se você NÃO enviar `ref_audio`, a API usa automaticamente o arquivo `voice.wav` como voz padrão!

## 1. Health Check

**Método:** GET  
**URL:** `http://localhost:8001/health`

---

## 2. Conversão com Voz Padrão (voice.wav)

**Método:** POST  
**URL:** `http://localhost:8001/api/v1/voice-conversion`  
**Body:** form-data

```
text: Olá! Este é um teste da API OmniVoice. A conversão de texto em fala está funcionando perfeitamente.
language: Portuguese
num_step: 32
guidance_scale: 2.0
denoise: true
speed: 1.0
```

**Nota:** Como não enviamos `ref_audio`, usa `voice.wav` automaticamente!

---

## 3. Com Clonagem de Voz Customizada

**Método:** POST  
**URL:** `http://localhost:8001/api/v1/voice-conversion`  
**Body:** form-data

```
text: Este áudio terá a voz clonada do arquivo de referência.
language: Portuguese
ref_audio: [ARQUIVO - mude tipo para File e selecione .wav ou .mp3]
ref_text: Transcrição do áudio de referência
num_step: 32
```

**Nota:** Aqui você ENVIA um `ref_audio` customizado, substituindo o `voice.wav` padrão.

---

## 4. Inglês (com voz padrão)

**Método:** POST  
**URL:** `http://localhost:8001/api/v1/voice-conversion`  
**Body:** form-data

```
text: Hello! This is a test of the OmniVoice API.
language: English
num_step: 32
```

---

## 5. Espanhol (com voz padrão)

**Método:** POST  
**URL:** `http://localhost:8001/api/v1/voice-conversion`  
**Body:** form-data

```
text: ¡Hola! Esta es una prueba de la API OmniVoice.
language: Spanish
num_step: 32
```

**Nota:** Todos os exemplos sem `ref_audio` usam `voice.wav` automaticamente!

---

## Decodificar Base64 para WAV (Python)

```python
import base64

audio_base64 = "COLE_AQUI_O_BASE64_DA_RESPOSTA"
audio_bytes = base64.b64decode(audio_base64)

with open("output.wav", "wb") as f:
    f.write(audio_bytes)
```

---

## Parâmetros Opcionais

```
num_step: 4-64 (padrão: 32)
guidance_scale: 0.0-4.0 (padrão: 2.0)
denoise: true/false (padrão: true)
speed: 0.5-1.5 (padrão: 1.0)
duration: segundos (opcional)
language: Portuguese, English, Spanish, French, etc. ou Auto
```
