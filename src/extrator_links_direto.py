import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def extrair_noticias_com_links():
    """Extrai notícias diretamente de sites moçambicanos com os links reais"""
    
    todas_noticias = []
    
    # ============================================================
    # 1. O País
    # ============================================================
    try:
        print("📰 A extrair do O País...")
        url = "https://opais.co.mz"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procurar artigos
        artigos = soup.find_all('div', class_=re.compile(r'td-module-container|post|article'))
        
        for artigo in artigos[:5]:
            try:
                # Título
                titulo_elem = artigo.find(['h2', 'h3'], class_=re.compile(r'title|entry-title'))
                if not titulo_elem:
                    titulo_elem = artigo.find('a')
                titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
                
                if not titulo or len(titulo) < 15:
                    continue
                
                # Link
                link = ""
                link_elem = artigo.find('a', href=True)
                if link_elem:
                    link = link_elem['href']
                    if link and not link.startswith('http'):
                        link = "https://opais.co.mz" + link
                
                # Descrição
                desc = ""
                desc_elem = artigo.find('p', class_=re.compile(r'excerpt|desc'))
                if desc_elem:
                    desc = desc_elem.get_text(strip=True)[:300]
                
                # Imagem
                img = ""
                img_elem = artigo.find('img')
                if img_elem and img_elem.get('src'):
                    img = img_elem['src']
                    if img.startswith('/'):
                        img = "https://opais.co.mz" + img
                
                todas_noticias.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:150],
                    "desc": desc if desc else "Clique para ler",
                    "img": img,
                    "video": "",
                    "tipo": "noticia",
                    "categoria": "Nacional",
                    "fonte": "O País",
                    "link_real": link
                })
                print(f"   ✅ {titulo[:50]}...")
            except:
                continue
    except Exception as e:
        print(f"   ⚠️ Erro O País: {e}")
    
    # ============================================================
    # 2. MZNews
    # ============================================================
    try:
        print("\n📰 A extrair do MZNews...")
        url = "https://mznews.co.mz"
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        artigos = soup.find_all('div', class_=re.compile(r'post|article|td-module'))
        
        for artigo in artigos[:5]:
            try:
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
                
                todas_noticias.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:150],
                    "desc": desc if desc else "Clique para ler",
                    "img": img,
                    "video": "",
                    "tipo": "noticia",
                    "categoria": "Nacional",
                    "fonte": "MZNews",
                    "link_real": link
                })
                print(f"   ✅ {titulo[:50]}...")
            except:
                continue
    except Exception as e:
        print(f"   ⚠️ Erro MZNews: {e}")
    
    # ============================================================
    # 3. DW Moçambique
    # ============================================================
    try:
        print("\n📰 A extrair da DW...")
        url = "https://www.dw.com/pt-002/not%C3%ADcias/s-13918"
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        artigos = soup.find_all('div', class_=re.compile(r'news-item|article|col-news'))
        
        for artigo in artigos[:5]:
            try:
                titulo_elem = artigo.find(['h2', 'h3'])
                titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
                
                if not titulo or len(titulo) < 15:
                    continue
                
                link = ""
                link_elem = artigo.find('a', href=True)
                if link_elem:
                    link = link_elem['href']
                    if link and not link.startswith('http'):
                        link = "https://www.dw.com" + link
                
                desc = ""
                desc_elem = artigo.find('p')
                if desc_elem:
                    desc = desc_elem.get_text(strip=True)[:300]
                
                todas_noticias.append({
                    "data": datetime.now().strftime("%d/%m/%Y"),
                    "titulo": titulo[:150],
                    "desc": desc if desc else "Clique para ler",
                    "img": "",
                    "video": "",
                    "tipo": "noticia",
                    "categoria": "Internacional",
                    "fonte": "DW",
                    "link_real": link
                })
                print(f"   ✅ {titulo[:50]}...")
            except:
                continue
    except Exception as e:
        print(f"   ⚠️ Erro DW: {e}")
    
    return todas_noticias

if __name__ == "__main__":
    print("="*50)
    print("🔍 EXTRAÇÃO DE NOTÍCIAS COM LINKS REAIS")
    print("="*50)
    
    noticias = extrair_noticias_com_links()
    
    print("\n" + "="*50)
    print(f"📊 Total de notícias extraídas: {len(noticias)}")
    
    # Salvar
    with open('noticias_links_reais.json', 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)
    
    print("✅ Arquivo salvo: noticias_links_reais.json")
    
    # Mostrar exemplos
    print("\n📰 EXEMPLOS COM LINKS REAIS:")
    for n in noticias[:5]:
        print(f"\n   Título: {n['titulo'][:60]}...")
        print(f"   Link: {n['link_real'][:80]}...")
