import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
from urllib.parse import urljoin

print("="*60)
print("🤖 ROBÔ DE NOTÍCIAS - Nampula é a Cena")
print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
print("="*60)

todas_noticias = []

def extrair_conteudo(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        titulo = ""
        titulo_elem = soup.find('h1')
        if not titulo_elem:
            titulo_elem = soup.find('title')
        if titulo_elem:
            titulo = titulo_elem.get_text(strip=True)
        
        desc = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content'].strip()
        else:
            og_desc = soup.find('meta', property='og:description')
            if og_desc and og_desc.get('content'):
                desc = og_desc['content'].strip()
        
        if not desc or len(desc) < 50:
            for p in soup.find_all('p'):
                texto = p.get_text(strip=True)
                if len(texto) > 80 and 'cookie' not in texto.lower():
                    desc = texto[:400]
                    break
        
        img = ""
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img = og_image['content']
        else:
            primeira_img = soup.find('img')
            if primeira_img and primeira_img.get('src'):
                img = primeira_img['src']
                if img.startswith('/'):
                    img = urljoin(url, img)
        
        return titulo, desc, img
    except:
        return "", "", ""

def extrair_dw():
    noticias = []
    try:
        print("\n📰 DW Moçambique...")
        url = "https://www.dw.com/pt-002/mo%C3%A7ambique/s-30380"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') and 'dw.com' in href and '/pt-002/' in href:
                if href not in links:
                    links.append(href)
        
        for link in links[:10]:
            titulo, desc, img = extrair_conteudo(link)
            if titulo and len(titulo) > 20:
                noticias.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:150],
                    "desc": desc[:400] if desc else "Clique para ler",
                    "img": img if img else "https://images.unsplash.com/photo-1529101091764-c3526daf3e8a?q=80&w=600",
                    "video": "",
                    "tipo": "noticia",
                    "categoria": "Nacional",
                    "fonte": "DW",
                    "link_real": link
                })
                print(f"  ✅ {titulo[:40]}...")
                time.sleep(0.5)
    except Exception as e:
        print(f"  ⚠️ Erro DW: {e}")
    return noticias

def extrair_bbc():
    noticias = []
    try:
        print("\n📰 BBC News...")
        url = "https://www.bbc.com/portuguese"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') and 'bbc.com' in href and '/portuguese' in href:
                if href not in links:
                    links.append(href)
        
        for link in links[:10]:
            titulo, desc, img = extrair_conteudo(link)
            if titulo and len(titulo) > 20:
                noticias.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:150],
                    "desc": desc[:400] if desc else "Clique para ler",
                    "img": img if img else "https://images.unsplash.com/photo-1529101091764-c3526daf3e8a?q=80&w=600",
                    "video": "",
                    "tipo": "noticia",
                    "categoria": "Internacional",
                    "fonte": "BBC",
                    "link_real": link
                })
                print(f"  ✅ {titulo[:40]}...")
                time.sleep(0.5)
    except Exception as e:
        print(f"  ⚠️ Erro BBC: {e}")
    return noticias

def main():
    todas = []
    todas.extend(extrair_dw())
    todas.extend(extrair_bbc())
    
    # Carregar notícias antigas
    try:
        with open('dados.json', 'r', encoding='utf-8') as f:
            antigas = json.load(f)
        titulos_novos = {n['titulo'] for n in todas}
        for n in antigas:
            if n['titulo'] not in titulos_novos:
                todas.append(n)
                titulos_novos.add(n['titulo'])
    except:
        pass
    
    # Salvar
    with open('dados.json', 'w', encoding='utf-8') as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 TOTAL: {len(todas)} notícias")
    print("="*60)

if __name__ == "__main__":
    main()
