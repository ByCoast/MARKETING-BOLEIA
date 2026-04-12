import time
import random
import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup
from browser import AntiBotBrowser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IGNORAR = ['menu', 'página', 'ir para', 'clique', 'buscar', 'cookies', 'aceitar', 'facebook', 'twitter', 'whatsapp', 'compartilhar']

class NewsScraper:
    def __init__(self, config):
        self.config = config
        self.all_news = []
        self.browser = None
    
    def _valido(self, title):
        if not title or len(title) < 15 or len(title) > 200:
            return False
        tl = title.lower()
        if any(p in tl for p in IGNORAR):
            return False
        if not title[0].isupper() and not title[0].isdigit():
            return False
        return True
    
    def _limpar_desc(self, text):
        if not text:
            return ""
        text = re.sub(r'(PARTILHAR|Compartilhar|Share|Facebook|Twitter|WhatsApp)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[▼▶•★☆]', '', text)
        return text.strip()[:400]
    
    def _extrair_imagem(self, container, soup):
        img = container.find('img')
        if img and img.get('src'):
            src = img.get('src')
            if src.startswith('http'):
                return src
            elif src.startswith('/'):
                return f"https://www.dw.com{src}"
        img = soup.find('img', class_=re.compile(r'(featured|main|article|post)'))
        if img and img.get('src'):
            src = img.get('src')
            if src.startswith('http'):
                return src
        return ""
    
    def _get_fonte(self, url, name):
        if 'dw.com' in url: return 'DW'
        elif 'voaportugues' in url: return 'VOA'
        elif 'bbc.com' in url: return 'BBC'
        elif 'aljazeera' in url: return 'Al Jazeera'
        elif 'opais.co.mz' in url: return 'O País'
        elif 'mznews.co.mz' in url: return 'MZNews'
        elif 'cartamz.com' in url: return 'Carta'
        elif 'verdade.co.mz' in url: return 'Verdade'
        elif 'njobs.co.mz' in url: return 'nJOBS'
        else: return name
    
    def run(self):
        self.browser = AntiBotBrowser()
        session = self.browser.start()
        if not session:
            return []
        try:
            for category, sites in self.config.items():
                if category == 'global' or not isinstance(sites, list):
                    continue
                logger.info(f"\n📂 {category}")
                for site in sites:
                    try:
                        url = site.get('url')
                        name = site.get('name')
                        html = self.browser.navigate(url)
                        if html:
                            soup = BeautifulSoup(html, 'html.parser')
                            noticias = []
                            containers = soup.find_all(['article', 'div', 'li'], limit=12)
                            for container in containers:
                                title_tag = container.find(['h2', 'h3', 'h4', 'h1'])
                                title = title_tag.get_text(strip=True) if title_tag else ""
                                if not self._valido(title):
                                    continue
                                desc = ""
                                desc_tag = container.find('p')
                                if desc_tag:
                                    desc = desc_tag.get_text(strip=True)
                                else:
                                    desc_div = container.find(['div'], class_=re.compile(r'(desc|excerpt|summary|content)'))
                                    if desc_div:
                                        desc = desc_div.get_text(strip=True)
                                desc = self._limpar_desc(desc)
                                if not desc:
                                    desc = "Clique para ler a notícia completa"
                                img = self._extrair_imagem(container, soup)
                                noticias.append({
                                    "data": datetime.now().strftime("%d/%m/%Y"),
                                    "titulo": title,
                                    "desc": desc,
                                    "img": img,
                                    "video": "",
                                    "tipo": "noticia",
                                    "categoria": category.capitalize(),
                                    "fonte": self._get_fonte(url, name)
                                })
                            unicos = []
                            vistos = set()
                            for n in noticias[:10]:
                                if n['titulo'] not in vistos:
                                    vistos.add(n['titulo'])
                                    unicos.append(n)
                            logger.info(f"  ✅ {name}: {len(unicos)} notícias")
                            self.all_news.extend(unicos)
                        time.sleep(2)
                    except Exception as e:
                        logger.error(f"  ❌ {site.get('name')}: {e}")
        finally:
            self.browser.quit()
        return self.all_news
