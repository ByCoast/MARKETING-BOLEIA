import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import logging
import time
import re
from datetime import datetime
from scraper_vagas import extrair_todas_vagas

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "DW Brasil": "https://rss.dw.com/rdf/rss-por",
    "BBC News Brasil": "https://feeds.bbci.co.uk/portuguese/rss.xml",
}

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?q=80&w=600"

def extrair_imagem_rss(item):
    for tag in ['media:content', 'enclosure']:
        elem = item.find(tag)
        if elem is not None:
            url = elem.get('url')
            if url and url.startswith('http'):
                return url
    return None

def fetch_rss_feed(feed_url, source_name):
    noticias = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(feed_url, headers=headers, timeout=20)
        root = ET.fromstring(response.content)
        items = root.findall('.//item') or root.findall('.//entry')
        for item in items[:15]:
            title_elem = item.find('title')
            title = title_elem.text if title_elem is not None else ""
            if not title or len(title) < 20:
                continue
            desc_elem = item.find('description') or item.find('summary')
            desc = desc_elem.text[:350] if desc_elem is not None else ""
            if desc:
                desc = re.sub(r'<[^>]+>', '', desc).strip()
            img = extrair_imagem_rss(item) or DEFAULT_IMAGE
            noticias.append({
                "data": datetime.now().strftime("%d/%m/%Y"),
                "titulo": title[:150],
                "desc": desc or "Clique para ler",
                "img": img,
                "video": "",
                "tipo": "noticia",
                "categoria": "Internacional",
                "fonte": source_name
            })
    except Exception as e:
        logger.error(f"Erro RSS {source_name}: {e}")
    return noticias

def extrair_miramar():
    noticias = []
    url = "https://miramar.co.mz/miramar-news"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            try:
                img = link.find('img')
                if not img:
                    continue
                src = img.get('src', '')
                if 'wp-content/uploads' not in src or 'logo' in src.lower():
                    continue
                src_limpa = re.sub(r'\?.*$', '', src)
                titulo = link.get('title', '') or link.get_text(strip=True)
                if not titulo or len(titulo) < 10:
                    next_h = link.find_next(['h2', 'h3', 'h4'])
                    if next_h:
                        titulo = next_h.get_text(strip=True)
                if not titulo or len(titulo) < 10:
                    continue
                desc = ""
                next_p = link.find_next('p')
                if next_p:
                    desc = next_p.get_text(strip=True)[:300]
                artigo_link = link.get('href', '')
                if artigo_link and not artigo_link.startswith('http'):
                    artigo_link = "https://miramar.co.mz" + artigo_link
                noticias.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:150],
                    "desc": desc if desc else "Clique para ler",
                    "img": src_limpa,
                    "video": "",
                    "tipo": "noticia",
                    "categoria": "Nacional",
                    "fonte": "Miramar News",
                    "link": artigo_link
                })
            except:
                continue
    except Exception as e:
        logger.error(f"Erro Miramar: {e}")
    return noticias

def main():
    logger.info("="*40)
    logger.info("Robô Completo - Notícias + Vagas")
    logger.info("="*40)
    todas = []
    for name, url in RSS_FEEDS.items():
        logger.info(f"📡 RSS: {name}")
        noticias = fetch_rss_feed(url, name)
        logger.info(f"   ✅ {len(noticias)} notícias")
        todas.extend(noticias)
        time.sleep(1)
    logger.info(f"📰 Miramar News")
    miramar = extrair_miramar()
    logger.info(f"   ✅ {len(miramar)} notícias")
    todas.extend(miramar)
    logger.info(f"💼 Vagas de emprego")
    vagas = extrair_todas_vagas()
    logger.info(f"   ✅ {len(vagas)} vagas")
    todas.extend(vagas)
    with open('data/dados.json', 'w', encoding='utf-8') as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)
    noticias_count = len([n for n in todas if n.get('tipo') == 'noticia'])
    vagas_count = len([n for n in todas if n.get('tipo') == 'vaga'])
    logger.info(f"📊 TOTAL: {len(todas)} itens")
    logger.info(f"   📰 Notícias: {noticias_count}")
    logger.info(f"   💼 Vagas: {vagas_count}")
    logger.info("="*40)

if __name__ == "__main__":
    main()
