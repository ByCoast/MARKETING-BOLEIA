import time
import random
import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup
from browser import AntiBotBrowser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IGNORAR = ['menu', 'página', 'ir para', 'clique', 'buscar', 'cookies', 'aceitar']

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
    
    def _get_fonte_from_url(self, url, name):
        """Extrai o nome da fonte baseado na URL"""
        if 'dw.com' in url:
            return 'DW'
        elif 'voaportugues' in url:
            return 'VOA'
        elif 'bbc.com' in url:
            return 'BBC'
        elif 'aljazeera' in url:
            return 'Al Jazeera'
        elif 'rfi.fr' in url:
            return 'RFI'
        elif 'opais.co.mz' in url:
            return 'O País'
        elif 'mznews.co.mz' in url:
            return 'MZNews'
        elif 'cartamz.com' in url:
            return 'Carta'
        elif 'verdade.co.mz' in url:
            return 'Verdade'
        elif 'mediafax.co.mz' in url:
            return 'MediaFax'
        elif 'njobs.co.mz' in url:
            return 'nJOBS'
        elif 'emprego.co.mz' in url:
            return 'Emprego.co.mz'
        else:
            return name
    
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
                            for tag in soup.find_all(['h2', 'h3', 'h4']):
                                title = tag.get_text(strip=True)
                                if self._valido(title):
                                    desc = ""
                                    p = tag.find_next('p')
                                    if p:
                                        desc = p.get_text(strip=True)[:300]
                                    noticias.append({
                                        "data": datetime.now().strftime("%d/%m/%Y"),
                                        "titulo": title,
                                        "desc": desc or "Clique para ler",
                                        "img": "",
                                        "video": "",
                                        "tipo": "noticia",
                                        "categoria": category.capitalize(),
                                        "fonte": self._get_fonte_from_url(url, name)
                                    })
                            unicos = []
                            vistos = set()
                            for n in noticias[:8]:
                                if n['titulo'] not in vistos:
                                    vistos.add(n['titulo'])
                                    unicos.append(n)
                            logger.info(f"  ✅ {name}: {len(unicos)}")
                            self.all_news.extend(unicos)
                        time.sleep(2)
                    except Exception as e:
                        logger.error(f"  ❌ {site.get('name')}: {e}")
        finally:
            self.browser.quit()
        return self.all_news
