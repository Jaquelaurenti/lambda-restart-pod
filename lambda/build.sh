#!/bin/bash
set -e

# Criar um diretório para dependências, se necessário
if [ -d "package" ]; then
    rm -rf package
fi
mkdir package

# Instalar dependências no diretório "package"
pip install -r requirements.txt -t ./package

# Ir para o diretório das dependências
cd package

# Compactar dependências
zip -r ../lambda_function.zip .

# Voltar e adicionar o código fonte ao zip
cd ..
zip -g lambda_function.zip src/lambda_function.py