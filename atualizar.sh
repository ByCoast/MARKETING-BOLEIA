#!/bin/bash
cd /data/data/com.termux/files/home/nampula-e-a-cena

git config user.name "ByCoast"
git config user.email "constantinopauloserras@gmail.com"

echo "🔄 Executando robô unificado (RSS + Miramar)..."
python src/scraper_unificado.py

echo "📤 Copiando dados.json para a raiz..."
cp data/dados.json ./dados.json

echo "📤 Enviando para o GitHub..."
git add data/dados.json dados.json logs/*.log
git commit -m "📰 Unificado: RSS + Miramar News - $(date +'%d/%m/%Y %H:%M')"
git push origin main

echo "✅ Concluído! Site atualizado."
