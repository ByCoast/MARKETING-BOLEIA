import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def extrair_opais():
    noticias = []
    try:
        url = "https://opais.co.mz"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for artigo in soup.find_all('div', class_=re.compile(r'td-module-container'))[:8]:
            titulo_elem = artigo.find(['h2', 'h3'])
            titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
            if not titulo or len(titulo) < 15:
                continue
            
            link = ""
            link_elem = artigo.find('a', href=True)
            if link_elem:
                link = link_elem['href']
                if link and not link.startswith('http'):
                    link = "https://opais.co.mz" + link
            
            desc = ""
            desc_elem = artigo.find('p')
            if desc_elem:
                desc = desc_elem.get_text(strip=True)[:300]
            
            img = ""
            img_elem = artigo.find('img')
            if img_elem and img_elem.get('src'):
                img = img_elem['src']
                if img.startswith('/'):
                    img = "https://opais.co.mz" + img
            
            noticias.append({
                "data": datetime.now().strftime("%d/%m/%Y"),
                "titulo": titulo[:150],
                "desc": desc if desc else "Clique para ler",
                "img": img,
                "tipo": "noticia",
                "categoria": "Nacional",
                "fonte": "O País",
                "link_real": link
            })
    except Exception as e:
        print(f"Erro O País: {e}")
    return noticias

def extrair_mznews():
    noticias = []
    try:
        url = "https://mznews.co.mz"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for artigo in soup.find_all('div', class_=re.compile(r'post'))[:8]:
            titulo_elem = artigo.find(['h2', 'h3'])
            titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
            if not titulo or len(titulo) < 15:
                continue
            
            link = ""
            link_elem = artigo.find('a', href=True)
            if link_elem:
                link = link_elem['href']
                if link and not link.startswith('http'):
                    link = "https://mznews.co.mz" + link
            
            desc = ""
            desc_elem = artigo.find('p')
            if desc_elem:
                desc = desc_elem.get_text(strip=True)[:300]
            
            img = ""
            img_elem = artigo.find('img')
            if img_elem and img_elem.get('src'):
                img = img_elem['src']
            
            noticias.append({
                "data": datetime.now().strftime("%d/%m/%Y"),
                "titulo": titulo[:150],
                "desc": desc if desc else "Clique para ler",
                "img": img,
                "tipo": "noticia",
                "categoria": "Nacional",
                "fonte": "MZNews",
                "link_real": link
            })
    except Exception as e:
        print(f"Erro MZNews: {e}")
    return noticias

def main():
    print("="*50)
    print("🚀 ROBÔ FINAL - Notícias Moçambique")
    print("="*50)
    
    todas = []
    
    print("\n📰 O País...")
    opais = extrair_opais()
    print(f"   ✅ {len(opais)} notícias")
    todas.extend(opais)
    
    print("\n📰 MZNews...")
    mznews = extrair_mznews()
    print(f"   ✅ {len(mznews)} notícias")
    todas.extend(mznews)
    
    with open('data/dados.json', 'w', encoding='utf-8') as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*50)
    print(f"📊 TOTAL: {len(todas)} notícias")
    print("✅ dados.json atualizado!")

if __name__ == "__main__":
    main()
