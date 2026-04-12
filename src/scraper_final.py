import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import logging
import time
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# 1. RSS FEEDS (BBC, DW)
# ============================================================
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

# ============================================================
# 2. MIRAMAR NEWS (Scraping com imagens reais)
# ============================================================
def extrair_miramar():
    noticias = []
    url = "https://miramar.co.mz/miramar-news"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links_com_imagem = soup.find_all('a', href=True)
        
        for link in links_com_imagem:
            try:
                img = link.find('img')
                if not img:
                    continue
                
                src = img.get('src', '')
                if 'wp-content/uploads' not in src:
                    continue
                if 'logo' in src.lower() or 'miramar_' in src.lower():
                    continue
                
                src_limpa = re.sub(r'\?.*$', '', src)
                
                titulo = link.get('title', '')
                if not titulo:
                    titulo = link.get_text(strip=True)
                if not titulo or len(titulo) < 5:
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
            except Exception:
                continue
    except Exception as e:
        logger.error(f"Erro Miramar: {e}")
    
    return noticias

# ============================================================
# 3. MAIN
# ============================================================
def main():
    logger.info("="*40)
    logger.info("Robô Final - RSS + Miramar News")
    logger.info("="*40)
    
    todas = []
    
    # RSS
    for name, url in RSS_FEEDS.items():
        logger.info(f"📡 RSS: {name}")
        noticias = fetch_rss_feed(url, name)
        logger.info(f"   ✅ {len(noticias)}")
        todas.extend(noticias)
        time.sleep(1)
    
    # Miramar
    logger.info(f"📰 Miramar News")
    miramar = extrair_miramar()
    logger.info(f"   ✅ {len(miramar)} notícias com imagens reais")
    todas.extend(miramar)
    
    # Salvar
    with open('data/dados.json', 'w', encoding='utf-8') as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)
    
    com_img_real = len([n for n in miramar if n['img']])
    logger.info(f"📊 TOTAL: {len(todas)} notícias")
    logger.info(f"📸 Miramar com imagem real: {com_img_real}/{len(miramar)}")
    logger.info("="*40)

if __name__ == "__main__":
    main()
