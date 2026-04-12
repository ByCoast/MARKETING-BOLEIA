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
    
    # Procurar por links que contêm imagens (a estrutura que vimos)
    links_com_imagem = soup.find_all('a', href=True)
    
    for link in links_com_imagem:
        try:
            # Verificar se tem imagem dentro
            img = link.find('img')
            if not img:
                continue
            
            src = img.get('src', '')
            # Filtrar apenas imagens de conteúdo (wp-content/uploads)
            if 'wp-content/uploads' not in src:
                continue
            # Ignorar logotipos
            if 'logo' in src.lower() or 'miramar_' in src.lower():
                continue
            
            # Limpar URL da imagem (remover parâmetros de resize)
            src_limpa = re.sub(r'\?.*$', '', src)
            
            # Título - procurar no link ou próximo
            titulo = link.get('title', '')
            if not titulo:
                # Procurar texto no link
                titulo = link.get_text(strip=True)
            if not titulo or len(titulo) < 5:
                # Procurar próximo título
                next_h = link.find_next(['h2', 'h3', 'h4'])
                if next_h:
                    titulo = next_h.get_text(strip=True)
            
            if not titulo or len(titulo) < 10:
                continue
            
            # Descrição - procurar próximo parágrafo
            desc = ""
            next_p = link.find_next('p')
            if next_p:
                desc = next_p.get_text(strip=True)[:300]
            
            # Link do artigo
            artigo_link = link.get('href', '')
            if artigo_link and not artigo_link.startswith('http'):
                artigo_link = "https://miramar.co.mz" + artigo_link
            
            noticias.append({
                "data": datetime.now().strftime("%d/%m/%Y"),
                "titulo": titulo[:150],
                "desc": desc if desc else "Clique para ler a notícia completa",
                "img": src_limpa,
                "video": "",
                "tipo": "noticia",
                "categoria": "Nacional",
                "fonte": "Miramar News",
                "link": artigo_link
            })
            print(f"  ✅ {titulo[:40]}... | Imagem: {src_limpa.split('/')[-1][:30]}")
            
        except Exception as e:
            continue
    
    return noticias

if __name__ == "__main__":
    noticias = extrair_miramar()
    print(f"\n📊 Total extraído: {len(noticias)} notícias")
    com_img = len([n for n in noticias if n['img']])
    print(f"📸 Com imagem real: {com_img}")
    
    # Salvar para debug
    with open('miramar_debug.json', 'w') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)
    print("✅ Debug salvo em miramar_debug.json")
