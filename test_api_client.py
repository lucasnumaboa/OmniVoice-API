#!/usr/bin/env python3
"""
Cliente de teste para a API OmniVoice.

Exemplos de uso da API REST.
"""

import base64
import requests
from pathlib import Path


def test_basic_tts(api_url: str = "http://localhost:8001"):
    """Teste básico de conversão de texto em fala."""
    print("=" * 60)
    print("Teste 1: Conversão básica de texto em fala")
    print("=" * 60)
    
    url = f"{api_url}/api/v1/voice-conversion"
    
    data = {
        "text": "Olá! Este é um teste da API OmniVoice. A conversão de texto em fala está funcionando perfeitamente.",
        "language": "Portuguese",
        "num_step": 32,
        "guidance_scale": 2.0,
        "denoise": True,
        "speed": 1.0
    }
    
    print(f"Enviando request para: {url}")
    print(f"Texto: {data['text'][:50]}...")
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        result = response.json()
        
        audio_bytes = base64.b64decode(result["audio_base64"])
        output_file = "output_basic.wav"
        
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        print(f"✅ Sucesso!")
        print(f"   - Áudio salvo em: {output_file}")
        print(f"   - Sample rate: {result['sample_rate']} Hz")
        print(f"   - Tamanho: {len(audio_bytes)} bytes")
        print(f"   - Mensagem: {result['message']}")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"   {response.text}")
    
    print()


def test_voice_cloning(api_url: str = "http://localhost:8001", ref_audio_path: str = None):
    """Teste de clonagem de voz com áudio de referência."""
    print("=" * 60)
    print("Teste 2: Clonagem de voz")
    print("=" * 60)
    
    if not ref_audio_path or not Path(ref_audio_path).exists():
        print("⚠️  Pulando teste de clonagem - arquivo de referência não fornecido")
        print(f"   Use: test_voice_cloning(ref_audio_path='caminho/para/audio.wav')")
        print()
        return
    
    url = f"{api_url}/api/v1/voice-conversion"
    
    data = {
        "text": "Este áudio foi gerado usando clonagem de voz. A voz deve ser similar ao áudio de referência.",
        "language": "Portuguese",
        "num_step": 32,
    }
    
    files = {
        "ref_audio": open(ref_audio_path, "rb")
    }
    
    print(f"Enviando request para: {url}")
    print(f"Áudio de referência: {ref_audio_path}")
    print(f"Texto: {data['text'][:50]}...")
    
    response = requests.post(url, data=data, files=files)
    
    if response.status_code == 200:
        result = response.json()
        
        audio_bytes = base64.b64decode(result["audio_base64"])
        output_file = "output_cloned.wav"
        
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        print(f"✅ Sucesso!")
        print(f"   - Áudio salvo em: {output_file}")
        print(f"   - Sample rate: {result['sample_rate']} Hz")
        print(f"   - Tamanho: {len(audio_bytes)} bytes")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"   {response.text}")
    
    print()


def test_different_languages(api_url: str = "http://localhost:8001"):
    """Teste com diferentes idiomas."""
    print("=" * 60)
    print("Teste 3: Múltiplos idiomas")
    print("=" * 60)
    
    url = f"{api_url}/api/v1/voice-conversion"
    
    tests = [
        ("English", "Hello! This is a test in English."),
        ("Spanish", "¡Hola! Esta es una prueba en español."),
        ("French", "Bonjour! Ceci est un test en français."),
    ]
    
    for i, (language, text) in enumerate(tests, 1):
        print(f"\n{i}. Testando {language}...")
        
        data = {
            "text": text,
            "language": language,
            "num_step": 32,
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            audio_bytes = base64.b64decode(result["audio_base64"])
            output_file = f"output_{language.lower()}.wav"
            
            with open(output_file, "wb") as f:
                f.write(audio_bytes)
            
            print(f"   ✅ Salvo em: {output_file}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    
    print()


def test_health_check(api_url: str = "http://localhost:8001"):
    """Teste do endpoint de health check."""
    print("=" * 60)
    print("Teste 0: Health Check")
    print("=" * 60)
    
    url = f"{api_url}/health"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API está funcionando!")
            print(f"   - Status: {result.get('status')}")
            print(f"   - Modelo carregado: {result.get('model_loaded')}")
        else:
            print(f"❌ Erro: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Não foi possível conectar à API em {api_url}")
        print(f"   Certifique-se de que a API está rodando!")
    
    print()


def main():
    """Executa todos os testes."""
    api_url = "http://localhost:8001"
    
    print("\n" + "=" * 60)
    print("CLIENTE DE TESTE - OmniVoice API")
    print("=" * 60)
    print(f"URL da API: {api_url}")
    print("=" * 60 + "\n")
    
    test_health_check(api_url)
    
    test_basic_tts(api_url)
    
    test_voice_cloning(api_url)
    
    test_different_languages(api_url)
    
    print("=" * 60)
    print("Testes concluídos!")
    print("=" * 60)
    print("\nVerifique os arquivos de áudio gerados:")
    print("  - output_basic.wav")
    print("  - output_cloned.wav (se forneceu áudio de referência)")
    print("  - output_english.wav")
    print("  - output_spanish.wav")
    print("  - output_french.wav")
    print()


if __name__ == "__main__":
    main()
