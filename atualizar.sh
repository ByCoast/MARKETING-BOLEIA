#!/bin/bash
cd /data/data/com.termux/files/home/nampula-e-a-cena
echo "🔄 Executando robô de notícias..."
python src/main.py
echo "📤 Enviando para o GitHub..."
git add dados.json
git commit -m "🔄 Notícias atualizadas em $(date +'%d/%m/%Y %H:%M')"
git push origin main
echo "✅ Concluído! Site atualizado."
