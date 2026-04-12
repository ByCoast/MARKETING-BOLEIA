import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime

def extrair_descricao_do_artigo(url_artigo):
    """Extrai a descrição da página do artigo - VERSÃO MELHORADA"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url_artigo, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remover elementos indesejados
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        
        # 1. Meta description (prioridade)
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content'].strip()
            if len(desc) > 30 and 'MIRAMAR' not in desc.upper() and 'Record' not in desc:
                return desc[:400]
        
        # 2. Og:description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            desc = og_desc['content'].strip()
            if len(desc) > 30 and 'MIRAMAR' not in desc.upper():
                return desc[:400]
        
        # 3. Primeiro parágrafo com conteúdo relevante
        # Procurar div de conteúdo principal
        content_div = soup.find('div', class_=re.compile(r'content|post|entry|article|text', re.I))
        if content_div:
            paragraphs = content_div.find_all('p')
            for p in paragraphs:
                texto = p.get_text(strip=True)
                if len(texto) > 80 and 'Instalar' not in texto and 'APP' not in texto and 'Cookie' not in texto:
                    return texto[:400]
        
        # 4. Qualquer parágrafo com mais de 100 caracteres
        all_p = soup.find_all('p')
        for p in all_p:
            texto = p.get_text(strip=True)
            if len(texto) > 100 and 'Instalar' not in texto and 'APP' not in texto:
                return texto[:400]
        
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
    
    # Filtrar links duplicados
    links_vistos = set()
    
    for link in links_com_imagem:
        try:
            artigo_link = link.get('href', '')
            if not artigo_link or 'miramar.co.mz' not in artigo_link:
                continue
            if artigo_link in links_vistos:
                continue
            links_vistos.add(artigo_link)
            
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
            if not titulo or len(titulo) < 10:
                titulo = link.get_text(strip=True)
            if not titulo or len(titulo) < 10:
                next_h = link.find_next(['h2', 'h3', 'h4'])
                if next_h:
                    titulo = next_h.get_text(strip=True)
            
            if not titulo or len(titulo) < 10:
                continue
            
            # Limpar título
            titulo = re.sub(r'Ver mais|Leia mais|Compartilhar', '', titulo).strip()
            
            print(f"  🔍 {artigo_link.split('/')[-2] if artigo_link.split('/') else '...'}...")
            descricao = extrair_descricao_do_artigo(artigo_link)
            time.sleep(0.3)
            
            if not descricao:
                descricao = "Clique para ler a notícia completa no site"
            
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
            print(f"     ✅ {titulo[:35]}... | Desc: {descricao[:40]}...")
            
        except Exception as e:
            continue
    
    return noticias

if __name__ == "__main__":
    print("📰 Miramar News - Extração definitiva")
    print("="*50)
    noticias = extrair_miramar()
    print("="*50)
    print(f"📊 Total: {len(noticias)} notícias")
    
    # Estatísticas de descrição
    com_desc = len([n for n in noticias if n['desc'] and 'Clique' not in n['desc']])
    print(f"📝 Com descrição real: {com_desc}/{len(noticias)}")
    
    with open('miramar_final.json', 'w') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)
    print("✅ Salvo em miramar_final.json")
