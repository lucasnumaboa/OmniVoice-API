#!/usr/bin/env python3
"""
Script para criar arquivo .env com configurações padrão.
"""

from pathlib import Path

ENV_CONTENT = """# OmniVoice API Configuration
# Configurações para a API FastAPI

# Porta do servidor API
API_PORT=8001

# Host do servidor (0.0.0.0 permite acesso externo, 127.0.0.1 apenas local)
API_HOST=0.0.0.0

# Modelo a ser carregado
MODEL_PATH=k2-fsa/OmniVoice

# Dispositivo (cuda, cpu, mps) - deixe vazio para auto-detecção
DEVICE=

# Criar link público via ngrok (true/false)
SHARE=false
"""

def main():
    env_file = Path(__file__).parent / ".env"
    
    if env_file.exists():
        print(f"⚠️  Arquivo .env já existe em: {env_file}")
        response = input("Deseja sobrescrever? (s/N): ").strip().lower()
        if response not in ('s', 'sim', 'y', 'yes'):
            print("❌ Operação cancelada.")
            return
    
    env_file.write_text(ENV_CONTENT, encoding='utf-8')
    print(f"✅ Arquivo .env criado com sucesso em: {env_file}")
    print("\nConfigurações padrão:")
    print("  - API_PORT=8001")
    print("  - API_HOST=0.0.0.0")
    print("  - MODEL_PATH=k2-fsa/OmniVoice")
    print("  - SHARE=false")
    print("\nEdite o arquivo .env para personalizar as configurações.")

if __name__ == "__main__":
    main()
