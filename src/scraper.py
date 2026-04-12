import time
import random
import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup
from browser import AntiBotBrowser

logger = logging.getLogger(__name__)

# Palavras a ignorar (títulos falsos)
IGNORAR_PALAVRAS = ['menu', 'página', 'ir para', 'clique aqui', 'acessar', 'buscar', 'pesquisar', 'cookies', 'aceitar']

class NewsScraper:
    def __init__(self, config):
        self.config = config
        self.all_news = []
        self.browser = None
    
    def run(self):
        self.browser = AntiBotBrowser()
        session = self.browser.start()
        
        if not session:
            return []
        
        try:
            for category, sites in self.config.items():
                if category == 'global':
                    continue
                if not isinstance(sites, list):
                    continue
                    
                logger.info(f"\n📂 Categoria: {category}")
                
                for site in sites:
                    try:
                        news = self._scrape_site(session, site, category)
                        self.all_news.extend(news)
                        time.sleep(random.uniform(2, 4))
                    except Exception as e:
                        logger.error(f"Erro em {site.get('name')}: {e}")
        finally:
            self.browser.quit()
        
        return self.all_news
    
    def _is_valid_title(self, title):
        """Verifica se o título é válido (não é lixo)"""
        if not title or len(title) < 15 or len(title) > 200:
            return False
        
        title_lower = title.lower()
        
        # Ignorar títulos com palavras proibidas
        for palavra in IGNORAR_PALAVRAS:
            if palavra in title_lower:
                return False
        
        # Deve começar com letra maiúscula (notícia geralmente começa assim)
        if not title[0].isupper() and not title[0].isdigit():
            return False
        
        # Não pode ser apenas números ou caracteres especiais
        if re.match(r'^[\d\W]+$', title):
            return False
        
        return True
    
    def _extract_from_dw(self, soup, category, fonte):
        """Extração específica para DW"""
        noticias = []
        # Procura os links de notícias da DW
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if '/pt-002/' in href and 's-' in href:
                title_elem = link.find(['h2', 'h3', 'h4', 'strong'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if self._is_valid_title(title):
                        noticias.append({
                            "data": datetime.now().strftime("%d/%m/%Y"),
                            "titulo": title,
                            "desc": "Clique no link para ler a notícia completa",
                            "img": "",
                            "video": "",
                            "tipo": "noticia",
                            "categoria": category.capitalize(),
                            "fonte": fonte,
                            "link": href if href.startswith('http') else f"https://www.dw.com{href}"
                        })
        return noticias
    
    def _extract_from_voa(self, soup, category, fonte):
        """Extração específica para VOA"""
        noticias = []
        for article in soup.find_all(['article', 'div'], class_=lambda x: x and ('media-block' in x or 'card' in x)):
            title_elem = article.find(['h4', 'h3', 'h2'])
            if title_elem:
                title = title_elem.get_text(strip=True)
                if self._is_valid_title(title):
                    desc_elem = article.find('p')
                    desc = desc_elem.get_text(strip=True)[:300] if desc_elem else ""
                    noticias.append({
                        "data": datetime.now().strftime("%d/%m/%Y"),
                        "titulo": title,
                        "desc": desc if desc else "Clique para ler",
                        "img": "",
                        "video": "",
                        "tipo": "noticia",
                        "categoria": category.capitalize(),
                        "fonte": fonte
                    })
        return noticias
    
    def _extract_generic(self, soup, category, fonte):
        """Extração genérica para outros sites"""
        noticias = []
        # Procura por tags comuns de título
        for title_tag in soup.find_all(['h2', 'h3', 'h4']):
            title = title_tag.get_text(strip=True)
            if self._is_valid_title(title):
                # Tenta encontrar o parágrafo próximo
                desc = ""
                parent = title_tag.find_parent()
                if parent:
                    p = parent.find('p')
                    if p:
                        desc = p.get_text(strip=True)[:300]
                
                noticias.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": title,
                    "desc": desc if desc else "Clique para ler",
                    "img": "",
                    "video": "",
                    "tipo": "noticia",
                    "categoria": category.capitalize(),
                    "fonte": fonte
                })
        return noticias
    
    def _scrape_site(self, session, site, category):
        name = site.get('name', 'desconhecido')
        url = site.get('url')
        
        if not url:
            return []
        
        try:
            html = self.browser.navigate(url)
            if not html:
                return []
                
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extração específica por fonte
            if 'dw.com' in url:
                noticias = self._extract_from_dw(soup, category, name)
            elif 'voaportugues' in url:
                noticias = self._extract_from_voa(soup, category, name)
            else:
                noticias = self._extract_generic(soup, category, name)
            
            # Limitar e remover duplicados por título
            unicos = []
            titulos_vistos = set()
            for n in noticias[:8]:
                if n['titulo'] not in titulos_vistos:
                    titulos_vistos.add(n['titulo'])
                    unicos.append(n)
            
            logger.info(f"  ✅ {name}: {len(unicos)} notícias")
            return unicos
            
        except Exception as e:
            logger.warning(f"  ⚠️ {name}: {str(e)[:80]}")
            return []
