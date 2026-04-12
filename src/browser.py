import time
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AntiBotBrowser:
    def __init__(self):
        self.session = None
    
    def start(self):
        logger.info("Iniciando cliente HTTP...")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/123.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-PT,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        logger.info("Cliente HTTP iniciado!")
        return self.session
    
    def navigate(self, url):
        logger.info(f"Acedendo: {url}")
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            time.sleep(2)
            return response.text
        except Exception as e:
            logger.error(f"Erro ao aceder {url}: {e}")
            return ""
    
    def quit(self):
        if self.session:
            self.session.close()
            logger.info("Cliente HTTP fechado")
