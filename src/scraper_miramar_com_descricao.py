import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime

def extrair_descricao_do_artigo(url_artigo):
    """Extrai a descrição da página do artigo"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url_artigo, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Tentar meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content'].strip()
            if len(desc) > 30 and 'MIRAMAR' not in desc.upper():
                return desc[:350]
        
        # 2. Tentar og:description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            desc = og_desc['content'].strip()
            if len(desc) > 30:
                return desc[:350]
        
        # 3. Procurar o primeiro parágrafo após o título
        titulo = soup.find(['h1', 'h2', 'h3'])
        if titulo:
            for _ in range(5):  # procurar nos próximos 5 elementos
                next_elem = titulo.find_next(['p', 'div'])
                if next_elem:
                    texto = next_elem.get_text(strip=True)
                    if len(texto) > 50 and 'Instalar' not in texto and 'APP' not in texto:
                        return texto[:350]
                    titulo = next_elem
        
        return ""
    except Exception as e:
        return ""

def extrair_miramar():
    url = "https://miramar.co.mz/miramar-news"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    noticias = []
    links_com_imagem = soup.find_all('a', href=True)
    
    total = 0
    for link in links_com_imagem:
        try:
            img = link.find('img')
            if not img:
                continue
            
            src = img.get('src', '')
            if 'wp-content/uploads' not in src:
                continue
            if 'logo' in src.lower() or 'miramar_' in src.lower():
                continue
            
            src_limpa = re.sub(r'\?.*$', '', src)
            
            titulo = link.get('title', '')
            if not titulo:
                titulo = link.get_text(strip=True)
            if not titulo or len(titulo) < 5:
                next_h = link.find_next(['h2', 'h3', 'h4'])
                if next_h:
                    titulo = next_h.get_text(strip=True)
            
            if not titulo or len(titulo) < 10:
                continue
            
            artigo_link = link.get('href', '')
            if artigo_link and not artigo_link.startswith('http'):
                artigo_link = "https://miramar.co.mz" + artigo_link
            
            # Extrair descrição da página do artigo
            print(f"  🔍 Acedendo: {artigo_link[:60]}...")
            descricao = extrair_descricao_do_artigo(artigo_link)
            time.sleep(0.5)  # Pausa para não sobrecarregar o servidor
            
            if not descricao:
                descricao = "Clique para ler a notícia completa"
            
            noticias.append({
                "data": datetime.now().strftime("%d/%m/%Y"),
                "titulo": titulo[:150],
                "desc": descricao,
                "img": src_limpa,
                "video": "",
                "tipo": "noticia",
                "categoria": "Nacional",
                "fonte": "Miramar News",
                "link": artigo_link
            })
            total += 1
            print(f"     ✅ {titulo[:40]}... | Descrição: {descricao[:50]}...")
            
        except Exception as e:
            continue
    
    return noticias

if __name__ == "__main__":
    print("📰 Iniciando extração do Miramar News com descrições...")
    noticias = extrair_miramar()
    print(f"\n📊 Total extraído: {len(noticias)} notícias")
    
    with open('miramar_com_descricao.json', 'w') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)
    print("✅ Salvo em miramar_com_descricao.json")
