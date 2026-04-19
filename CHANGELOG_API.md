# Changelog - API OmniVoice

## ✨ Nova Funcionalidade: Voz Padrão Automática

### O que mudou?

Agora a API usa **automaticamente** o arquivo `voice.wav` como voz de referência quando você **NÃO** envia o parâmetro `ref_audio`.

### Como funciona?

1. **SEM ref_audio** → Usa `voice.wav` automaticamente
2. **COM ref_audio** → Usa o arquivo que você enviou

### Exemplos:

#### Exemplo 1: Usando voz padrão (voice.wav)
```
POST http://localhost:8001/api/v1/voice-conversion

Body (form-data):
text: Olá, este texto usará a voz do arquivo voice.wav
language: Portuguese
```
✅ Usa `voice.wav` automaticamente!

#### Exemplo 2: Usando voz customizada
```
POST http://localhost:8001/api/v1/voice-conversion

Body (form-data):
text: Este texto usará a voz que eu enviei
language: Portuguese
ref_audio: [seu_arquivo.wav]
```
✅ Usa o arquivo que você enviou!

### Localização do arquivo padrão

O arquivo `voice.wav` deve estar em:
```
f:\OmniVoice\OmniVoice\voice.wav
```

### Vantagens

✅ Não precisa enviar `ref_audio` toda vez  
✅ Voz consistente em todas as requisições  
✅ Mais rápido e simples de usar  
✅ Ainda pode customizar enviando `ref_audio` quando quiser  

### Documentação atualizada

- `api.py` - Lógica implementada
- `POSTMAN_TESTE.md` - Exemplos atualizados
- Swagger docs em `/docs` - Documentação automática atualizada
