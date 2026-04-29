#!/usr/bin/env python3
"""
robofinal.py — Robô completo v4.0
Nampula é a Cena | ByCoast
─────────────────────────────────────────────
Metas:
  ✅ 800+ Notícias (Política, Economia, Sociedade, Cultura, Desporto)
  ✅ 400+ Vagas de emprego
  ✅ 300+ Bolada (Tecnologia e Inovação)
  ✅ Classificação por TIPO e CATEGORIA
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urljoin
import difflib
import os

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
MAX_ITENS     = 2000      # Aumentado para 2000
MAX_POR_FONTE = 40        # Aumentado para 40
TIMEOUT       = 20
DELAY         = 0.3
LOG_FILE      = "log.txt"
DADOS_FILE    = "dados.json"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept-Language': 'pt-PT,pt;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

IMG_NOTICIAS = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&q=70"
IMG_VAGAS    = "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=600&q=70"
IMG_TECH     = "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&q=70"

# ─────────────────────────────────────────────
# LOG
# ─────────────────────────────────────────────
log_linhas = []

def log(msg, emoji=""):
    linha = f"{emoji} {msg}".strip()
    print(linha)
    log_linhas.append(f"[{datetime.now().strftime('%H:%M:%S')}] {linha}")

def salvar_log():
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*55}\n")
        f.write(f"EXECUCAO: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write('\n'.join(log_linhas) + '\n')

# ─────────────────────────────────────────────
# DEDUPLICACAO INTELIGENTE
# ─────────────────────────────────────────────
titulos_vistos = []

def ja_existe(titulo_novo, limiar=0.82):
    t = titulo_novo.lower().strip()
    for t2 in titulos_vistos:
        if difflib.SequenceMatcher(None, t, t2).ratio() >= limiar:
            return True
    return False

def registar_titulo(titulo):
    titulos_vistos.append(titulo.lower().strip())

# ─────────────────────────────────────────────
# DETECTAR TIPO (noticia / vaga / bolada)
# ─────────────────────────────────────────────
def detectar_tipo(titulo, desc, fonte=""):
    texto = (titulo + " " + desc).lower()
    
    # Bolada (tecnologia, gadgets, inovação)
    palavras_bolada = [
        'tecnologia', 'app', 'smartphone', 'iphone', 'android', 
        'software', 'internet', '5g', 'ia', 'inteligência artificial',
        'gadget', 'lançamento', 'starlink', 'drone', 'laptop', 
        'tablet', 'inovação', 'digital', 'robô', 'aplicativo',
        'windows', 'linux', 'mac', 'computador', 'notebook',
        'inteligencia artificial', 'chatgpt', 'openai', 'bits', 'bytes'
    ]
    if any(p in texto for p in palavras_bolada):
        return "bolada"
    
    # Vaga (emprego, recrutamento)
    palavras_vaga = [
        'vaga', 'emprego', 'recruta', 'contrata', 'oportunidade',
        'trabalho', 'estágio', 'salário', 'candidato', 'seleção',
        'rh', 'recrutamento', 'empregos', 'contratação', 'curriculum'
    ]
    if any(p in texto for p in palavras_vaga) or fonte in ["nJOBS","MaisVagas","WizAndroid Emprego","VagasMoz","EmpregoMoz"]:
        return "vaga"
    
    # Notícia (padrão)
    return "noticia"

# ─────────────────────────────────────────────
# CATEGORIAS INTELIGENTES
# ─────────────────────────────────────────────
CATEGORIAS = {
    "Tecnologia":    ['tecnolog','inteligencia artificial',' ia ','software','app','android',
                      'iphone','google','microsoft','samsung','startup','internet',
                      'cibersegur','hacker','digital','robot','programac','dados','computad'],
    "Economia":      ['economi','negocio','financ','banco','investimento','mercado','bolsa',
                      'inflacao','divida','exportacao','importacao','empresa','comercio',
                      'moeda','dolar','metical','pib','taxa','imposto'],
    "Saude":         ['saude','hospital','medic','doenca','covid','malaria','vacina',
                      'pandemia','virus','clinica','medicina','farmac','enfermei'],
    "Politica":      ['politi','governo','eleicao','presidente','ministro','parlamento',
                      'partido','frelimo','renamo','deputado','estado','nacoes unidas',
                      'onu','diplomacia','embaixada','senado','assembleia'],
    "Educacao":      ['educa','escola','universidade','estudante','aluno','ensino',
                      'professor','bolsa de estudo','formacao','curso','faculdade'],
    "Seguranca":     ['segur','crime','polici','ataque','guerra','terroris','conflito',
                      'cabo delgado','insurgente','militar','morto','vitima','assalto'],
    "Desporto":      ['desport','futebol','jogo','campeonat','equipa','atleta',
                      'olimpiadas','mundial','liga','golo','basquete','boxe'],
    "Internacional": ['eua','estados unidos','trump','europa','china','russia','brasil',
                      'angola','africa do sul','guerra na','otan','nato','franca','alemanha'],
    "Ambiente":      ['climat','ambiente','carbono','aquecimento','ciclone','inundacao',
                      'seca','floresta','energia solar','renovavel','poluicao'],
    "Emprego":       ['vaga','emprego','recruta','contrata','trabalho','carreira',
                      'candidatura','estagio','salario','rh ','recursos humanos'],
    "Sociedade":     ['social','comunidade','familia','mulher','crianca','jovem',
                      'pobreza','habitacao','agua','fome','migrante','refugiado'],
    "Nacional":      ['mocambique','maputo','nampula','beira','tete','quelimane',
                      'inhambane','chimoio','lichinga','pemba'],
    "Cultura":       ['cultura','arte','musica','cinema','teatro','literatura',
                      'pintura','escultura','dança','tradição','festival'],
}

def detectar_categoria(titulo, desc="", fonte=""):
    texto = re.sub(r'[áàãâä]','a', re.sub(r'[éèê]','e', re.sub(r'[íì]','i',
            re.sub(r'[óòõô]','o', re.sub(r'[úùü]','u',
            (titulo+" "+desc).lower()))))).strip()
    scores = {}
    for cat, palavras in CATEGORIAS.items():
        score = sum(1 for p in palavras if p in texto)
        if score > 0:
            scores[cat] = score
    if scores:
        return max(scores, key=scores.get)
    if fonte in ["BBC","DW","G1 Globo","SAPO","TecMundo","ITForum","Olhar Digital","Canaltech"]:
        return "Internacional"
    if fonte in ["nJOBS","MaisVagas","WizAndroid Emprego","VagasMoz","EmpregoMoz","JobMoz"]:
        return "Emprego"
    if fonte in ["ITForum","TecMundo","WizAndroid","TechMoz","StartupMoz"]:
        return "Tecnologia"
    return "Nacional"

# ─────────────────────────────────────────────
# RESUMO COM IA (Claude Haiku — rapido e barato)
# ─────────────────────────────────────────────
def resumir_com_ia(titulo, desc_original):
    if not desc_original or len(desc_original) < 80:
        return desc_original
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        frases = re.split(r'(?<=[.!?])\s+', desc_original.strip())
        return ' '.join(frases[:3])[:450]
    try:
        prompt = (
            "Escreve um resumo jornalistico conciso (3 frases, max 380 caracteres) "
            "em portugues de Mocambique sobre este artigo. "
            "Comeca directamente com o facto principal. "
            "Nao uses 'Este artigo' ou 'O texto'.\n\n"
            f"Titulo: {titulo}\nConteudo: {desc_original[:700]}\n\nResumo:"
        )
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 180,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15
        )
        if resp.status_code == 200:
            resumo = resp.json()['content'][0]['text'].strip()
            if len(resumo) > 40:
                return resumo
    except:
        pass
    frases = re.split(r'(?<=[.!?])\s+', desc_original.strip())
    return ' '.join(frases[:3])[:450]

# ─────────────────────────────────────────────
# EXTRAIR IMAGEM REAL DO ARTIGO
# ─────────────────────────────────────────────
def extrair_imagem_real(soup, url_base, fallback):
    og = soup.find('meta', property='og:image')
    if og and og.get('content','').startswith('http'):
        return og['content'].strip()
    tw = soup.find('meta', attrs={'name':'twitter:image'})
    if tw and tw.get('content','').startswith('http'):
        return tw['content'].strip()
    for img_tag in soup.find_all('img'):
        src = img_tag.get('src') or img_tag.get('data-src','')
        if not src:
            continue
        if not src.startswith('http'):
            src = urljoin(url_base, src)
        if any(ext in src.lower() for ext in ['.jpg','.jpeg','.png','.webp']):
            if not any(x in src.lower() for x in ['logo','icon','avatar','sprite']):
                return src
    return fallback

# ─────────────────────────────────────────────
# EXTRAIR CONTEUDO COMPLETO DE UM ARTIGO
# ─────────────────────────────────────────────
def extrair_artigo(url, img_fallback=IMG_NOTICIAS):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(r.text, 'html.parser')

        titulo = ""
        for tag, attrs in [('h1',{}),('meta',{'property':'og:title'}),
                           ('meta',{'name':'title'}),('title',{})]:
            el = soup.find(tag, attrs)
            if el:
                titulo = el.get('content','') or el.get_text(strip=True)
                titulo = re.sub(r'\s*[|\-–—]\s*.+$','',titulo).strip()
                if len(titulo) > 10:
                    break

        desc = ""
        for tag, attrs in [('meta',{'name':'description'}),
                           ('meta',{'property':'og:description'}),
                           ('meta',{'name':'twitter:description'})]:
            el = soup.find(tag, attrs)
            if el and el.get('content') and len(el['content']) > 40:
                desc = el['content'].strip()
                break
        if len(desc) < 100:
            parags = []
            for p in soup.find_all('p'):
                t = p.get_text(' ', strip=True)
                if len(t) > 60 and not any(x in t.lower() for x in ['cookie','javascript','privacy']):
                    parags.append(t)
                if len(' '.join(parags)) > 600:
                    break
            if parags:
                desc = ' '.join(parags)[:700]

        img = extrair_imagem_real(soup, url, img_fallback)

        data = datetime.now().strftime("%d/%m/%Y")
        for tag, attrs in [('meta',{'property':'article:published_time'}),
                           ('meta',{'name':'publishdate'}),
                           ('meta',{'property':'og:updated_time'})]:
            el = soup.find(tag, attrs)
            if el and el.get('content'):
                try:
                    dt = datetime.fromisoformat(el['content'].replace('Z','+00:00'))
                    data = dt.strftime("%d/%m/%Y")
                    break
                except:
                    pass

        return titulo.strip()[:160], desc.strip()[:700], img, data
    except:
        return "", "", img_fallback, datetime.now().strftime("%d/%m/%Y")

# ─────────────────────────────────────────────
# EXTRAIR VIA RSS
# ─────────────────────────────────────────────
def extrair_rss(nome, rss_url, tipo_padrao="noticia", fonte="", img_fallback=IMG_NOTICIAS):
    items = []
    try:
        log(f"{nome} (RSS)...", "📡")
        r = requests.get(rss_url, headers=HEADERS, timeout=TIMEOUT)
        root = ET.fromstring(r.content)
        canal = root.find('channel') or root
        entradas = canal.findall('item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        log(f"  {len(entradas)} entradas")

        for entry in entradas[:MAX_POR_FONTE]:
            titulo_el = entry.find('title')
            if not titulo_el or not titulo_el.text:
                continue
            titulo = titulo_el.text.strip()[:160]
            if len(titulo) < 12 or ja_existe(titulo):
                continue

            desc = ""
            for tag in ['description','summary',
                        '{http://www.w3.org/2005/Atom}summary',
                        '{http://www.w3.org/2005/Atom}content']:
                el = entry.find(tag)
                if el is not None and el.text:
                    desc = BeautifulSoup(el.text,'html.parser').get_text(' ').strip()[:700]
                    break

            link = ""
            link_el = entry.find('link')
            if link_el is not None:
                link = (link_el.text or link_el.get('href','')).strip()

            img = img_fallback
            for tag in ['enclosure',
                        '{http://search.yahoo.com/mrss/}content',
                        '{http://search.yahoo.com/mrss/}thumbnail']:
                el = entry.find(tag)
                if el is not None:
                    c = el.get('url','')
                    if c and any(x in c.lower() for x in ['.jpg','.jpeg','.png','.webp']):
                        img = c
                        break
            if img == img_fallback and link:
                try:
                    r2 = requests.get(link, headers=HEADERS, timeout=10)
                    s2 = BeautifulSoup(r2.text,'html.parser')
                    img = extrair_imagem_real(s2, link, img_fallback)
                except:
                    pass

            data = datetime.now().strftime("%d/%m/%Y")
            for tag in ['pubDate','published','{http://www.w3.org/2005/Atom}published']:
                el = entry.find(tag)
                if el is not None and el.text:
                    try:
                        raw = el.text.strip()
                        for fmt in ["%a, %d %b %Y %H:%M:%S %z",
                                    "%a, %d %b %Y %H:%M:%S %Z",
                                    "%Y-%m-%dT%H:%M:%S%z",
                                    "%Y-%m-%dT%H:%M:%SZ"]:
                            try:
                                data = datetime.strptime(raw[:30],fmt).strftime("%d/%m/%Y")
                                break
                            except:
                                continue
                    except:
                        pass
                    break

            desc = resumir_com_ia(titulo, desc)
            tipo_detectado = detectar_tipo(titulo, desc, fonte or nome)
            cat = detectar_categoria(titulo, desc, fonte or nome)
            registar_titulo(titulo)

            item = {
                "data": data, "titulo": titulo,
                "desc": desc or "Clique para ler o artigo completo.",
                "img": img, "video": "",
                "tipo": tipo_detectado, "categoria": cat,
                "fonte": fonte or nome, "link_real": link
            }
            if tipo_detectado == "vaga":
                item["link_vaga"] = link

            items.append(item)
            log(f"  ✅ [{tipo_detectado}/{cat}] {titulo[:40]}...")
            time.sleep(DELAY)

    except Exception as e:
        log(f"  ⚠️ Erro RSS {nome}: {e}")
    return items

# ─────────────────────────────────────────────
# EXTRAIR VIA HTML
# ─────────────────────────────────────────────
def extrair_html(nome, base_url, filtro_url, tipo_padrao="noticia", fonte="",
                 img_fallback=IMG_NOTICIAS, max_links=25):
    items = []
    try:
        log(f"{nome} (HTML)...", "🌐")
        r = requests.get(base_url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(r.text, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if not href.startswith('http'):
                href = urljoin(base_url, href)
            if filtro_url(href) and href not in links:
                links.append(href)
        log(f"  {len(links)} links encontrados")

        for link in links[:max_links]:
            titulo, desc, img, data = extrair_artigo(link, img_fallback)
            if not titulo or len(titulo) < 12 or ja_existe(titulo):
                continue
            desc = resumir_com_ia(titulo, desc)
            tipo_detectado = detectar_tipo(titulo, desc, fonte or nome)
            cat = detectar_categoria(titulo, desc, fonte or nome)
            registar_titulo(titulo)

            item = {
                "data": data, "titulo": titulo,
                "desc": desc or "Clique para ler o artigo completo.",
                "img": img, "video": "",
                "tipo": tipo_detectado, "categoria": cat,
                "fonte": fonte or nome, "link_real": link
            }
            if tipo_detectado == "vaga":
                item["link_vaga"] = link

            items.append(item)
            log(f"  ✅ [{tipo_detectado}/{cat}] {titulo[:40]}...")
            time.sleep(DELAY)

    except Exception as e:
        log(f"  ⚠️ Erro HTML {nome}: {e}")
    return items

# ════════════════════════════════════════════════════════════
# TODAS AS FONTES (EXPANDIDO PARA METAS)
# ════════════════════════════════════════════════════════════

def extrair_noticias():
    """Fontes para atingir 800+ notícias"""
    n = []
    
    # Fontes internacionais
    n += extrair_rss("DW Mocambique","https://rss.dw.com/rdf/rss-pt-moc",fonte="DW")
    n += extrair_rss("BBC Portugues","https://feeds.bbci.co.uk/portuguese/rss.xml",fonte="BBC")
    
    # Fontes Moçambicanas
    n += extrair_html("Jornal Noticias","https://jornalnoticias.co.mz",
        filtro_url=lambda h:'jornalnoticias.co.mz' in h and len(h.split('/'))>5,
        fonte="Jornal Noticias")
    n += extrair_html("MZNews","https://mznews.co.mz/en/",
        filtro_url=lambda h:'mznews.co.mz' in h and len(h.split('/'))>4,
        fonte="MZNews")
    n += extrair_html("CanalMoz","https://canalmoz.co.mz",
        filtro_url=lambda h:'canalmoz.co.mz' in h,
        fonte="CanalMoz")
    n += extrair_html("Verdade","https://verdade.co.mz",
        filtro_url=lambda h:'verdade.co.mz' in h,
        fonte="Verdade")
    n += extrair_html("Carta","https://cartamz.com",
        filtro_url=lambda h:'cartamz.com' in h,
        fonte="Carta")
    n += extrair_html("O País","https://opais.co.mz",
        filtro_url=lambda h:'opais.co.mz' in h,
        fonte="O País")
    
    # Fontes portuguesas (com notícias internacionais)
    n += extrair_html("SAPO","https://sapo.pt",
        filtro_url=lambda h:'sapo.pt' in h and '/noticias/' in h,
        fonte="SAPO")
    n += extrair_html("G1 Globo","https://g1.globo.com/",
        filtro_url=lambda h:'g1.globo.com' in h and '.ghtml' in h and '/mundo/' in h,
        fonte="G1 Globo")
    
    return n

def extrair_bolada():
    """Fontes para atingir 300+ bolada (tecnologia/inovação)"""
    b = []
    
    # Tecnologia internacional
    b += extrair_rss("ITForum","https://itforum.com.br/feed/",fonte="ITForum",img_fallback=IMG_TECH)
    b += extrair_rss("TecMundo","https://rss.tecmundo.com.br/feed",fonte="TecMundo",img_fallback=IMG_TECH)
    b += extrair_rss("Olhar Digital","https://olhardigital.com.br/feed/",fonte="Olhar Digital",img_fallback=IMG_TECH)
    b += extrair_rss("Canaltech","https://canaltech.com.br/rss/",fonte="Canaltech",img_fallback=IMG_TECH)
    
    # Tecnologia Moçambicana
    b += extrair_html("WizAndroid Tech","https://wizandroidmz.com",
        filtro_url=lambda h:'wizandroidmz.com' in h and len(h.split('/'))>4 and 'emprego' not in h,
        fonte="WizAndroid",img_fallback=IMG_TECH)
    b += extrair_html("TechMoz","https://techmoz.com",
        filtro_url=lambda h:'techmoz.com' in h,
        fonte="TechMoz",img_fallback=IMG_TECH)
    b += extrair_html("StartupMoz","https://startupmoz.co.mz",
        filtro_url=lambda h:'startupmoz.co.mz' in h,
        fonte="StartupMoz",img_fallback=IMG_TECH)
    
    return b

def extrair_vagas():
    """Fontes para atingir 400+ vagas"""
    v = []
    
    v += extrair_html("nJobs","https://njobs.co.mz",
        filtro_url=lambda h:'njobs.co.mz' in h and any(x in h.lower() for x in ['vaga','job','emprego']),
        tipo_padrao="vaga",fonte="nJOBS",img_fallback=IMG_VAGAS,max_links=30)
    
    v += extrair_html("MaisVagas","https://maisvagas.co.mz",
        filtro_url=lambda h:'maisvagas.co.mz' in h and len(h.split('/'))>4,
        tipo_padrao="vaga",fonte="MaisVagas",img_fallback=IMG_VAGAS,max_links=30)
    
    v += extrair_html("WizAndroid Emprego","https://wizandroidmz.com/emprego/",
        filtro_url=lambda h:'wizandroidmz.com' in h and 'emprego' in h and len(h.split('/'))>5,
        tipo_padrao="vaga",fonte="WizAndroid Emprego",img_fallback=IMG_VAGAS,max_links=25)
    
    v += extrair_html("VagasMoz","https://vagasmoz.com",
        filtro_url=lambda h:'vagasmoz.com' in h and 'vaga' in h.lower(),
        tipo_padrao="vaga",fonte="VagasMoz",img_fallback=IMG_VAGAS,max_links=25)
    
    v += extrair_html("EmpregoMoz","https://empregomoz.co.mz",
        filtro_url=lambda h:'empregomoz.co.mz' in h,
        tipo_padrao="vaga",fonte="EmpregoMoz",img_fallback=IMG_VAGAS,max_links=25)
    
    return v

# ════════════════════════════════════════════════════════════
# GIT PUSH
# ════════════════════════════════════════════════════════════
def git_push(n_novos):
    log("A publicar no GitHub...", "🚀")
    for cmd in [
        ["git","add","dados.json",LOG_FILE],
        ["git","commit","-m",f"🤖 Auto-update: {n_novos} novos — {datetime.now().strftime('%d/%m/%Y %H:%M')}"],
        ["git","push"]
    ]:
        r = subprocess.run(cmd, capture_output=True, text=True)
        saida = r.stdout.strip() or r.stderr.strip()
        ok = r.returncode==0 or "nothing to commit" in saida
        log(f"  {'✅' if ok else '⚠️'} {' '.join(cmd[:2])}")
    log("Site actualizado!", "🌐")

# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
def main():
    print("="*60)
    print("🤖 ROBO v4.0 — Nampula e a Cena")
    print(f"   🎯 Metas: 800+ Notícias | 400+ Vagas | 300+ Bolada")
    print(f"   Fontes: DW · BBC · JN · MZNews · CanalMoz · Verdade")
    print(f"   Carta · O País · SAPO · G1 · ITForum · TecMundo")
    print(f"   Olhar Digital · Canaltech · WizAndroid · TechMoz")
    print(f"   nJobs · MaisVagas · VagasMoz · EmpregoMoz")
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*60)

    # Carregar antigos
    antigos = []
    try:
        with open(DADOS_FILE,'r',encoding='utf-8') as f:
            antigos = json.load(f)
        for item in antigos:
            if item.get('titulo'):
                registar_titulo(item['titulo'])
        log(f"Carregados {len(antigos)} itens existentes","📂")
    except:
        log("A comecar do zero","📂")

    # Recolher
    log("\n── NOTICIAS ──────────────────────────────","📰")
    novos = extrair_noticias()
    log("\n── BOLADA (Tecnologia/Inovação) ─────────","💻")
    novos += extrair_bolada()
    log("\n── VAGAS ─────────────────────────────────","💼")
    novos += extrair_vagas()

    n_novos = len(novos)

    # Mesclar
    titulos_novos = {n['titulo'] for n in novos}
    antigos_ok = [a for a in antigos if a.get('titulo') not in titulos_novos]
    final = (novos + antigos_ok)[:MAX_ITENS]

    # Guardar
    with open(DADOS_FILE,'w',encoding='utf-8') as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    # Stats por TIPO
    n_not = len([x for x in final if x.get('tipo')=='noticia'])
    n_bol = len([x for x in final if x.get('tipo')=='bolada'])
    n_vag = len([x for x in final if x.get('tipo')=='vaga'])
    
    # Stats por CATEGORIA
    cats = {}
    for x in final:
        c = x.get('categoria','Outros')
        cats[c] = cats.get(c,0)+1

    print("\n"+"="*60)
    log(f"✅ CONCLUIDO!","✅")
    log(f"  📰 Novos recolhidos : {n_novos}")
    log(f"  📰 Total noticias   : {n_not} (Meta: 800) → {'✅' if n_not>=800 else f'⚠️ Faltam {800-n_not}'}")
    log(f"  💼 Total vagas      : {n_vag} (Meta: 400) → {'✅' if n_vag>=400 else f'⚠️ Faltam {400-n_vag}'}")
    log(f"  💻 Total bolada     : {n_bol} (Meta: 300) → {'✅' if n_bol>=300 else f'⚠️ Faltam {300-n_bol}'}")
    log(f"  📦 Total no JSON    : {len(final)}/{MAX_ITENS}")
    log(f"\n  📊 CATEGORIAS:")
    for cat,count in sorted(cats.items(),key=lambda x:-x[1])[:15]:
        log(f"     {cat}: {count}")
    print("="*60)

    salvar_log()
    git_push(n_novos)

if __name__ == "__main__":
    main()