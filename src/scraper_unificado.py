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
# 1. FEEDS RSS (BBC, DW)
# ============================================================
RSS_FEEDS = {
    "DW Brasil": "https://rss.dw.com/rdf/rss-por",
    "BBC News Brasil": "https://feeds.bbci.co.uk/portuguese/rss.xml",
}

# Imagem padrão apenas para RSS (fallback)
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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
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
        logger.error(f"Erro no RSS {source_name}: {e}")
    return noticias

# ============================================================
# 2. MIRAMAR NEWS (Scraping direto com imagens reais)
# ============================================================
def extrair_miramar():
    noticias = []
    url = "https://miramar.co.mz/miramar-news"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procurar por divs que contêm notícias
        artigos = soup.find_all('div', class_=lambda x: x and ('post' in str(x).lower() or 'item' in str(x).lower()))
        if not artigos:
            artigos = soup.find_all('article')
        if not artigos:
            artigos = soup.find_all('li', class_=lambda x: x and ('post' in str(x).lower()))
        
        logger.info(f"Miramar: {len(artigos)} artigos encontrados")
        
        for artigo in artigos[:15]:
            try:
                # Título
                titulo_elem = artigo.find(['h2', 'h3', 'h4', 'h5'])
                if not titulo_elem:
                    titulo_elem = artigo.find('a', class_=lambda x: x and 'title' in str(x).lower())
                if not titulo_elem:
                    titulo_elem = artigo.find('a')
                
                titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
                
                if not titulo or len(titulo) < 15:
                    continue
                
                # Limpar título
                titulo = re.sub(r'Ver mais|Leia mais|Compartilhar', '', titulo).strip()
                
                # ===== IMAGEM REAL =====
                img = ""
                img_elem = artigo.find('img')
                if img_elem and img_elem.get('src'):
                    img = img_elem['src']
                    if img.startswith('/'):
                        img = "https://miramar.co.mz" + img
                    # Garantir que é imagem real (não logo)
                    if 'logo' in img.lower() or 'icon' in img.lower():
                        img = ""
                
                # Se não encontrou, procurar imagem no link
                if not img:
                    link_img = artigo.find('a', class_=lambda x: x and 'image' in str(x).lower())
                    if link_img and link_img.find('img'):
                        img = link_img.find('img').get('src', '')
                        if img and img.startswith('/'):
                            img = "https://miramar.co.mz" + img
                
                # ===== DESCRIÇÃO =====
                desc = ""
                desc_elem = artigo.find('p')
                if desc_elem:
                    desc = desc_elem.get_text(strip=True)
                else:
                    desc_div = artigo.find('div', class_=lambda x: x and ('desc' in str(x).lower() or 'excerpt' in str(x).lower()))
                    if desc_div:
                        desc = desc_div.get_text(strip=True)
                
                if desc:
                    desc = re.sub(r'Ver mais|Leia mais|Compartilhar', '', desc).strip()
                    desc = desc[:350] + "..." if len(desc) > 350 else desc
                else:
                    desc = "Clique para ler a notícia completa"
                
                # ===== LINK =====
                link = ""
                link_elem = artigo.find('a', href=True)
                if link_elem:
                    link = link_elem['href']
                    if link and not link.startswith('http'):
                        link = "https://miramar.co.mz" + link
                
                # Se não encontrou imagem real, NÃO usa fallback do Unsplash
                # Deixa vazio para o site usar imagem padrão
                
                noticias.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:150],
                    "desc": desc,
                    "img": img,  # Pode ser vazio, o site usa imagem padrão
                    "video": "",
                    "tipo": "noticia",
                    "categoria": "Nacional",
                    "fonte": "Miramar News",
                    "link": link
                })
                logger.info(f"  ✅ {titulo[:40]}... | Imagem: {'Sim' if img else 'Não'}")
            except Exception as e:
                continue
    except Exception as e:
        logger.error(f"Erro Miramar: {e}")
    
    return noticias

# ============================================================
# 3. CARREGAR NOTÍCIAS ANTIGAS (para preservar)
# ============================================================
def carregar_antigas():
    try:
        with open('data/dados.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# ============================================================
# 4. MAIN
# ============================================================
def main():
    logger.info("="*40)
    logger.info("Robô Unificado - RSS + Miramar News")
    logger.info("="*40)
    
    todas = []
    
    # RSS Feeds
    for name, url in RSS_FEEDS.items():
        logger.info(f"📡 RSS: {name}")
        noticias = fetch_rss_feed(url, name)
        logger.info(f"   ✅ {len(noticias)} notícias")
        todas.extend(noticias)
        time.sleep(1)
    
    # Miramar News (com imagens reais)
    logger.info(f"📰 Scraping: Miramar News")
    miramar = extrair_miramar()
    logger.info(f"   ✅ {len(miramar)} notícias com imagens reais")
    todas.extend(miramar)
    
    # Carregar notícias antigas e mesclar (preservar as que têm imagens)
    antigas = carregar_antigas()
    titulos_novos = {n['titulo'] for n in todas}
    for n in antigas:
        if n['titulo'] not in titulos_novos:
            todas.append(n)
            titulos_novos.add(n['titulo'])
    
    # Salvar
    with open('data/dados.json', 'w', encoding='utf-8') as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)
    
    # Estatísticas
    com_imagem = len([n for n in todas if n['img'] and 'unsplash' not in n['img']])
    logger.info(f"📊 TOTAL: {len(todas)} notícias")
    logger.info(f"📸 Com imagem real: {com_imagem}")
    logger.info("="*40)

if __name__ == "__main__":
    main()
