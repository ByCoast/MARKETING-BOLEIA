import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def extrair_miramar():
    url = "https://miramar.co.mz/miramar-news"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    noticias = []
    
    # Procurar por artigos
    artigos = soup.find_all(['article', 'div'], class_=re.compile(r'post|item|news|article'))
    
    for artigo in artigos[:15]:
        try:
            # Título
            titulo_elem = artigo.find(['h2', 'h3', 'h4'])
            if not titulo_elem:
                titulo_elem = artigo.find('a', class_=re.compile(r'title'))
            titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
            
            if not titulo or len(titulo) < 15:
                continue
            
            # Imagem - procurar especificamente dentro do artigo
            img = ""
            img_elem = artigo.find('img')
            if img_elem and img_elem.get('src'):
                src = img_elem['src']
                if 'wp-content/uploads' in src and 'logo' not in src.lower():
                    img = src if src.startswith('http') else f"https://miramar.co.mz{src}"
            
            # Se não encontrou imagem no artigo, procurar no link de imagem
            if not img:
                link_img = artigo.find('a', class_=re.compile(r'image|thumbnail'))
                if link_img and link_img.find('img'):
                    src = link_img.find('img').get('src', '')
                    if 'wp-content/uploads' in src:
                        img = src if src.startswith('http') else f"https://miramar.co.mz{src}"
            
            # Descrição
            desc = ""
            desc_elem = artigo.find('p')
            if desc_elem:
                desc = desc_elem.get_text(strip=True)[:300]
            
            # Link
            link_elem = artigo.find('a', href=True)
            link = link_elem['href'] if link_elem else ""
            if link and not link.startswith('http'):
                link = f"https://miramar.co.mz{link}"
            
            noticias.append({
                "data": datetime.now().strftime("%d/%m/%Y"),
                "titulo": titulo[:150],
                "desc": desc or "Clique para ler",
                "img": img,
                "video": "",
                "tipo": "noticia",
                "categoria": "Nacional",
                "fonte": "Miramar News",
                "link": link
            })
        except Exception as e:
            continue
    
    return noticias

if __name__ == "__main__":
    noticias = extrair_miramar()
    print(json.dumps(noticias, indent=2, ensure_ascii=False))
    print(f"\n📊 Total: {len(noticias)} notícias")
    com_img = len([n for n in noticias if n['img']])
    print(f"📸 Com imagem: {com_img}")
