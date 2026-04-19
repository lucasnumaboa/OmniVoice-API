@echo off
echo =========================================
echo Iniciando a API OmniVoice...
echo =========================================
echo.

cd /d "%~dp0"

REM Verificar se o arquivo .env existe, se não, criar
if not exist ".env" (
    echo Arquivo .env nao encontrado. Criando com configuracoes padrao...
    python create_env.py
    echo.
)

echo Carregando configuracoes do arquivo .env...
echo.

python -m omnivoice.api

pause
