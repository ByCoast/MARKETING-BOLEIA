import requests
import xml.etree.ElementTree as ET
import logging
import json
import time
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Feeds RSS ---
RSS_FEEDS = {
    "BBC News Brasil": "https://feeds.bbci.co.uk/portuguese/rss.xml",
    "DW Brasil": "https://rss.dw.com/rdf/rss-por",
    "RFI Português": "https://www.rfi.fr/pt/rss",
}

# --- Mapeamento de Categorias por Palavras-chave ---
KEYWORD_TO_CATEGORY = {
    'economia': 'Economia', 'mercado': 'Economia', 'negócios': 'Economia', 'finanças': 'Economia', 'petróleo': 'Economia',
    'tecnologia': 'Tecnologia', 'digital': 'Tecnologia', 'internet': 'Tecnologia', 'app': 'Tecnologia', 'ia': 'Tecnologia', 'inteligência': 'Tecnologia',
    'saúde': 'Saúde', 'hospital': 'Saúde', 'médico': 'Saúde', 'doença': 'Saúde', 'covid': 'Saúde',
    'guerra': 'Conflito Internacional', 'ataque': 'Conflito Internacional', 'míssil': 'Conflito Internacional', 'bombardeio': 'Conflito Internacional',
    'trump': 'Política', 'lula': 'Política', 'eleição': 'Política', 'governo': 'Política',
    'futebol': 'Desporto', 'campeonato': 'Desporto', 'liga': 'Desporto', 'mundial': 'Desporto', 'jogo': 'Desporto',
    'cultura': 'Cultura', 'arte': 'Cultura', 'música': 'Cultura', 'livro': 'Cultura', 'cinema': 'Cultura',
    'clima': 'Ambiente', 'tempestade': 'Ambiente', 'ciclone': 'Ambiente', 'cheia': 'Ambiente', 'inundação': 'Ambiente',
    'emprego': 'Emprego', 'vaga': 'Emprego', 'trabalho': 'Emprego', 'carreira': 'Emprego', 'recrutamento': 'Emprego',
}

# --- Imagens padrão por categoria ---
CATEGORY_IMAGES = {
    "Economia": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=600",
    "Tecnologia": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?q=80&w=600",
    "Saúde": "https://images.unsplash.com/photo-1584515933487-779824d29309?q=80&w=600",
    "Política": "https://images.unsplash.com/photo-1529101091764-c3526daf3e8a?q=80&w=600",
    "Conflito Internacional": "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=600",
    "Desporto": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?q=80&w=600",
    "Cultura": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?q=80&w=600",
    "Ambiente": "https://images.unsplash.com/photo-1509391366360-2e959784a276?q=80&w=600",
    "Emprego": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=600",
    "Sociedade": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?q=80&w=600",
    "Educação": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=600",
    "Internacional": "https://images.unsplash.com/photo-1529101091764-c3526daf3e8a?q=80&w=600",
}
DEFAULT_IMAGE = "https://images.unsplash.com/photo-1582213782179-e0d53f98f2ca?q=80&w=600"

def get_category_and_image(title):
    title_lower = title.lower()
    for key, category in KEYWORD_TO_CATEGORY.items():
        if key in title_lower:
            img = CATEGORY_IMAGES.get(category, DEFAULT_IMAGE)
            return category, img
    return "Internacional", CATEGORY_IMAGES.get("Internacional", DEFAULT_IMAGE)

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\[.*?\]', '', text)
    return text.strip()

def fetch_rss_feed(feed_url, source_name):
    noticias = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(feed_url, headers=headers, timeout=20)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        items = root.findall('.//item') or root.findall('.//entry')
        logger.info(f"📡 Processando {source_name}: {len(items)} itens encontrados.")
        for item in items[:20]:
            title_elem = item.find('title')
            title = clean_text(title_elem.text) if title_elem is not None else None
            if not title or len(title) < 20:
                continue
            desc_elem = item.find('description') or item.find('summary')
            desc = clean_text(desc_elem.text) if desc_elem is not None else ""
            desc = desc[:400] + "..." if len(desc) > 400 else desc
            if not desc:
                desc = "Clique para ler a notícia completa."
            category, image_url = get_category_and_image(title)
            
            # Determinar o tipo (noticia, vaga, bolada)
            tipo = "noticia"
            if any(p in title.lower() for p in ['vaga', 'emprego', 'recrutamento', 'oportunidade', 'contrata']):
                tipo = "vaga"
            elif any(p in title.lower() for p in ['lançamento', 'preço', 'promoção', 'desconto', 'novo', 'actual']):
                tipo = "bolada"
            
            noticias.append({
                "data": datetime.now().strftime("%d/%m/%Y"),
                "titulo": title,
                "desc": desc,
                "img": image_url,
                "video": "",
                "tipo": tipo,
                "categoria": category,
                "fonte": source_name
            })
    except Exception as e:
        logger.error(f"❌ Erro no feed {source_name}: {e}")
    return noticias

def main():
    logger.info("="*40)
    logger.info("Iniciando Robô de Notícias com RSS")
    logger.info("="*40)
    todas_as_noticias = []
    for name, url in RSS_FEEDS.items():
        logger.info(f"--- Buscando: {name} ---")
        noticias = fetch_rss_feed(url, name)
        todas_as_noticias.extend(noticias)
        time.sleep(1)
    logger.info(f"✅ Total de itens coletados: {len(todas_as_noticias)}")
    
    # Carregar notícias antigas para manter histórico
    try:
        with open('data/dados.json', 'r', encoding='utf-8') as f:
            antigas = json.load(f)
        logger.info(f"📚 Notícias antigas carregadas: {len(antigas)}")
        # Combinar e remover duplicados por título
        titulos_novos = {n['titulo'] for n in todas_as_noticias}
        for n in antigas:
            if n['titulo'] not in titulos_novos:
                todas_as_noticias.append(n)
                titulos_novos.add(n['titulo'])
    except:
        pass
    
    logger.info(f"📊 Total final: {len(todas_as_noticias)} itens")
    
    output_file = 'data/dados.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(todas_as_noticias, f, ensure_ascii=False, indent=2)
    logger.info(f"💾 Dados salvos em '{output_file}'")

if __name__ == "__main__":
    main()
