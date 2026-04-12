#!/usr/bin/env python3
import sys
import os
import json
import yaml
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def carregar_config():
    with open('config/sites.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def carregar_json():
    try:
        with open('data/dados.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def salvar_json(dados):
    with open('data/dados.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    logger.info(f"Salvo: {len(dados)} artigos no total")

def main():
    logger.info("=" * 40)
    logger.info("Robô de Notícias - Iniciado")
    logger.info("=" * 40)
    
    config = carregar_config()
    
    from scraper import NewsScraper
    scraper = NewsScraper(config)
    novas = scraper.run()
    
    logger.info(f"\n📊 Total de novas notícias: {len(novas)}")
    
    existentes = carregar_json()
    
    titulos_existentes = {n.get('titulo') for n in existentes}
    unicas = [n for n in novas if n.get('titulo') not in titulos_existentes]
    
    todas = unicas + existentes
    salvar_json(todas[:500])
    
    logger.info(f"✅ Adicionadas {len(unicas)} notícias novas")
    logger.info("=" * 40)

if __name__ == "__main__":
    main()
