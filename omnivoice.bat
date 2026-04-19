@echo off
title OmniVoice Server
echo =========================================
echo Iniciando o servidor OmniVoice...
echo Diretorio: F:\OmniVoice\OmniVoice\omnivoice
echo =========================================

:: Muda para a unidade F:
F:

:: Acessa o diretório do projeto
cd "F:\OmniVoice\OmniVoice\omnivoice"

:: Executa o comando de inicialização
omnivoice-demo --ip 0.0.0.0 --port 8001

:: Pausa o terminal caso o servidor feche ou dê erro (para você conseguir ler a mensagem)
pause