import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extrair_noticias_miramar():
    url = "https://miramar.co.mz/miramar-news"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    noticias = []
    
    # Procurar por elementos que parecem notícias (WordPress)
    # Método 1: Procurar por divs com classe 'post' ou 'news-item'
    artigos = soup.find_all('div', class_=lambda x: x and ('post' in x or 'news' in x or 'item' in x or 'col' in x))
    
    if not artigos:
        # Método 2: Procurar por li com classes específicas
        artigos = soup.find_all('li', class_=lambda x: x and ('post' in x or 'news' in x))
    
    if not artigos:
        # Método 3: Procurar por article
        artigos = soup.find_all('article')
    
    if not artigos:
        # Método 4: Procurar por divs com imagens
        artigos = soup.find_all('div', class_=lambda x: x and ('thumbnail' in x or 'image' in x))
    
    logger.info(f"Encontrados {len(artigos)} possíveis artigos")
    
    for artigo in artigos[:20]:
        try:
            # Título
            titulo_elem = artigo.find(['h2', 'h3', 'h4', 'h5', 'a'])
            if titulo_elem:
                titulo = titulo_elem.get_text(strip=True)
            else:
                titulo = ""
            
            if not titulo or len(titulo) < 15:
                continue
            
            # Limpar título (remover "Ver mais" e lixo)
            titulo = titulo.replace('Ver mais', '').replace('Leia mais', '').strip()
            
            # Imagem - procurar em vários lugares
            img = ""
            img_elem = artigo.find('img')
            if img_elem and img_elem.get('src'):
                img = img_elem['src']
                if img.startswith('/'):
                    img = "https://miramar.co.mz" + img
                # Ignorar imagens muito pequenas ou logotipos
                if 'logo' in img.lower() or 'icon' in img.lower() or img.endswith('.svg'):
                    img = ""
            
            # Se não encontrou imagem no artigo, procurar na página
            if not img:
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    img = og_image['content']
            
            # Descrição
            desc = ""
            desc_elem = artigo.find('p')
            if desc_elem:
                desc = desc_elem.get_text(strip=True)
            else:
                # Procurar por div com descrição
                desc_div = artigo.find('div', class_=lambda x: x and ('desc' in str(x).lower() or 'excerpt' in str(x).lower()))
                if desc_div:
                    desc = desc_div.get_text(strip=True)
            
            # Limpar descrição
            if desc:
                desc = desc.replace('Ver mais', '').replace('Leia mais', '').strip()
                desc = desc[:350] + "..." if len(desc) > 350 else desc
            
            if not desc:
                desc = "Clique para ler a notícia completa"
            
            # Link
            link = ""
            link_elem = artigo.find('a', href=True)
            if link_elem:
                link = link_elem['href']
                if link and not link.startswith('http'):
                    link = "https://miramar.co.mz" + link
            
            if not link:
                # Tenta encontrar link no título
                if titulo_elem and titulo_elem.name == 'a' and titulo_elem.get('href'):
                    link = titulo_elem['href']
            
            # Categoria baseada na URL
            categoria = "Nacional"
            if '/videos/' in link:
                categoria = "Vídeos"
            elif '/politica/' in link:
                categoria = "Política"
            elif '/economia/' in link:
                categoria = "Economia"
            
            noticias.append({
                "data": datetime.now().strftime("%d/%m/%Y"),
                "titulo": titulo[:150],
                "desc": desc,
                "img": img,
                "video": "",
                "tipo": "noticia",
                "categoria": categoria,
                "fonte": "Miramar News",
                "link": link
            })
            logger.info(f"  ✅ {titulo[:50]}... | Imagem: {'Sim' if img else 'Não'}")
            
        except Exception as e:
            logger.warning(f"Erro: {e}")
    
    return noticias

if __name__ == "__main__":
    noticias = extrair_noticias_miramar()
    print(json.dumps(noticias, indent=2, ensure_ascii=False))
    print(f"\n📊 Total: {len(noticias)} notícias extraídas")
