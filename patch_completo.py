#!/usr/bin/env python3
"""
patch_completo.py — Aplica TODAS as melhorias de uma vez:
- Data visível nos cards
- Imagens por categoria
- Formatação de descrições (parágrafos, lead)
- Destaque com imagem de fundo
- Filtro Tudo com mix de notícias + boladas (sem vagas)
"""

import subprocess
import re
from datetime import datetime

FICHEIRO = "index.html"

print("="*60)
print("🎨 PATCH COMPLETO — Nampula é a Cena")
print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("="*60)

with open(FICHEIRO, 'r', encoding='utf-8') as f:
    html = f.read()

original = html

# ============================================================
# 1. IMAGENS POR CATEGORIA (FALLBACK)
# ============================================================

if 'const IMG_CAT' not in html:
    IMG_CAT = """
// IMAGENS FALLBACK POR CATEGORIA
const IMG_CAT = {
  'Tecnologia':    'https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&q=70',
  'Economia':      'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&q=70',
  'Saúde':         'https://images.unsplash.com/photo-1584820927498-cfe5211fd8bf?w=600&q=70',
  'Política':      'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=600&q=70',
  'Educação':      'https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=600&q=70',
  'Segurança':     'https://images.unsplash.com/photo-1601597111158-2fceff292cdc?w=600&q=70',
  'Desporto':      'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=600&q=70',
  'Internacional': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&q=70',
  'Ambiente':      'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=600&q=70',
  'Emprego':       'https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=600&q=70',
  'Sociedade':     'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=600&q=70',
  'Nacional':      'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600&q=70',
};
function imgFallback(item){
  return IMG_CAT[item.categoria] || IMG_CAT['Nacional'] || 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&q=70';
}
"""
    # Inserir antes de buildCard
    if 'function buildCard' in html:
        html = html.replace('function buildCard', IMG_CAT + '\nfunction buildCard')
        print("✅ Imagens por categoria adicionadas")
else:
    print("✅ Imagens por categoria já existem")

# ============================================================
# 2. FORMATAR DESCRIÇÃO (formatarDesc)
# ============================================================

if 'function formatarDesc' not in html:
    FORMATAR = """
// FORMATAR DESCRIÇÃO EM PARÁGRAFOS
function formatarDesc(texto){
  if(!texto || texto.length < 10) return '<p>Clique para ler mais.</p>';
  texto = texto.replace(/\\s+/g, ' ').trim();
  const frases = texto.match(/[^.!?…]+[.!?…]+/g) || [texto];
  const paragrafos = [];
  let grupo = [];
  frases.forEach((f, i) => {
    grupo.push(f.trim());
    if(grupo.length >= 2 || i === frases.length - 1){
      paragrafos.push(grupo.join(' '));
      grupo = [];
    }
  });
  let html = '';
  if(paragrafos.length > 0){
    const lead = paragrafos.shift();
    html += `<p class="art-lead">${lead}</p>`;
  }
  paragrafos.forEach(p => {
    if(p.trim().length > 10) html += `<p>${p.trim()}</p>`;
  });
  return html || `<p>${texto}</p>`;
}
"""
    # Inserir antes de buildCard
    if 'function buildCard' in html:
        html = html.replace('function buildCard', FORMATAR + '\nfunction buildCard')
        print("✅ formatarDesc adicionada")
else:
    print("✅ formatarDesc já existe")

# ============================================================
# 3. ATUALIZAR buildCard (data visível + fallback)
# ============================================================

# Verificar se o buildCard já usa as melhorias
if 'c-date-overlay' not in html:
    # Buscar o buildCard atual e substituir
    padrao_build = r'(function buildCard\(item,i\)\{)(.*?)(\n\})'
    match = re.search(padrao_build, html, re.DOTALL)
    if match:
        novo_build = """function buildCard(item,i){
  const cls=item.tipo==='vaga'?'item-vaga':item.tipo==='bolada'?'item-bolada':'';
  const cat=item.categoria||item.tipo;
  const fallback=imgFallback(item);
  const data=item.data||'';
  const thumb=item.video
    ?`<div class="c-thumb" style="display:flex;align-items:center;justify-content:center;background:#0d0d0d;"><i class="fas fa-play-circle" style="font-size:48px;color:rgba(255,255,255,.45);"></i><span class="c-tag">${cat}</span></div>`
    :`<div class="c-thumb"><img src="${item.img||fallback}" loading="lazy" onerror="this.src='${fallback}'"><span class="c-tag">${cat}</span>${data?`<span class="c-date-overlay">📅 ${data}</span>`:''}</div>`;
  const body=item.video?`<video controls style="width:100%;margin-bottom:14px;"><source src="${item.video}" type="video/mp4"></video>`:'';
  return`<article class="card ${cls}" style="animation-delay:${i*.07}s">
    <div onclick="toggleAc(this)" class="faq-header">
      ${thumb}
      <div class="c-body">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:7px;">
          <span class="c-cat">${cat}</span>
          ${data?`<time class="c-time">📅 ${data}</time>`:''}
        </div>
        <h3 class="c-title">${item.titulo}</h3>
        <div class="c-footer">
          <span class="c-read">Ler mais <i class="fas fa-chevron-down exp-ic" style="font-size:9px;"></i></span>
        </div>
      </div>
    </div>
    <div class="faq-content">
      <div class="faq-body">
        ${body}
        <div class="art-body">${formatarDesc(item.desc)}</div>
        ${item.link_vaga?`<a href="${item.link_vaga}" target="_blank" class="btn-apply">📩 Candidatar Agora</a>`:''}
        <a href="https://wa.me/?text=*${encodeURIComponent('Vê no Nampula é a Cena:')}* ${encodeURIComponent(item.titulo)}" target="_blank" class="btn-share">📱 Partilhar</a>
      </div>
    </div>
  </article>`;
}"""
        html = html.replace(match.group(0), novo_build)
        print("✅ buildCard atualizado (com data e fallback)")
    else:
        print("⚠️ buildCard não encontrado")
else:
    print("✅ buildCard já atualizado")

# ============================================================
# 4. CSS DO DESTAQUE
# ============================================================

if '.destaque-inner::before' not in html:
    estilos_destaque = """
/* DESTAQUE COM IMAGEM DE FUNDO */
.destaque-inner::before{
  content:'';position:absolute;inset:0;
  background-image:var(--dest-img,none);
  background-size:cover;background-position:center;
  filter:brightness(.35);z-index:0;
}
.destaque-inner::after{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(200,32,43,.3) 0%,rgba(10,10,15,.85) 80%);
  z-index:1;
}
.destaque-img-wrap{display:none;}
.destaque-body{position:relative;z-index:2;padding:28px 24px;min-height:260px;}
.destaque-titulo{font-family:'Oswald',sans-serif;font-size:clamp(20px,4vw,30px);color:#fff;text-shadow:0 1px 10px rgba(0,0,0,.5);}
.destaque-desc{color:rgba(255,255,255,.75);}
.destaque-ler{background:var(--red);color:#fff;border:none;padding:11px 22px;cursor:pointer;}
.destaque-ler:hover{background:var(--red2);}
"""
    if '</style>' in html:
        html = html.replace('</style>', estilos_destaque + '\n</style>')
        print("✅ CSS do destaque adicionado")
else:
    print("✅ CSS do destaque já existe")

# ============================================================
# 5. FUNÇÃO mostrarDestaque (com imagem de fundo)
# ============================================================

if '--dest-img' not in html:
    padrao_mostrar = r'(function mostrarDestaque\(item\)\{)(.*?)(\n\})'
    match = re.search(padrao_mostrar, html, re.DOTALL)
    if match:
        novo_mostrar = """function mostrarDestaque(item){
  const inner=document.getElementById('destaque-inner');
  if(item.img && item.img.startsWith('http')){
    inner.style.setProperty('--dest-img', `url('${item.img}')`);
  } else {
    inner.style.setProperty('--dest-img', `url('${imgFallback(item)}')`);
  }
  document.getElementById('destaque-cat').textContent=item.categoria||item.tipo;
  document.getElementById('destaque-data').textContent=item.data||'';
  document.getElementById('destaque-titulo').textContent=item.titulo;
  const frasesDest=(item.desc||'').match(/[^.!?]+[.!?]+/g)||[];
  const resumo=frasesDest.slice(0,2).join(' ').trim()||((item.desc||'').substring(0,160));
  document.getElementById('destaque-desc').textContent=resumo;
  document.getElementById('destaque-wrap').style.display='block';
  document.getElementById('destaque-btn').onclick=()=>{
    const tab=document.querySelector(`.tab[data-tipo="${item.tipo}"]`);
    if(tab)mudarFeed(tab);
    setTimeout(()=>window.scrollTo({top:document.getElementById('feed-home').offsetTop-80}),300);
  };
}"""
        html = html.replace(match.group(0), novo_mostrar)
        print("✅ mostrarDestaque atualizada (com imagem de fundo)")
    else:
        print("⚠️ mostrarDestaque não encontrada")
else:
    print("✅ mostrarDestaque já atualizada")

# ============================================================
# 6. FILTRO TUDO (mix sem vagas)
# ============================================================

# 6.1 Feed inicial
linha_inicial = "renderFeed('feed-home', dadosBase.filter(i=>i.tipo==='noticia'), 9);"
if linha_inicial in html:
    html = html.replace(linha_inicial, "renderFeed('feed-home', dadosBase.filter(i=>i.tipo!=='vaga'));")
    print("✅ Feed inicial corrigido (mix sem vagas)")

# 6.2 Função mudarFeed
padrao_mudar = r'(function mudarFeed\(tab\)\{)(.*?)(\n\})'
match = re.search(padrao_mudar, html, re.DOTALL)
if match:
    nova_mudar = """function mudarFeed(tab){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  tab.classList.add('active');
  tipoAtivo=tab.getAttribute('data-tipo');
  actualizarFiltrosHome();
  if(tipoAtivo==='noticia'){
    renderFeed('feed-home', dadosBase.filter(i=>i.tipo!=='vaga'));
  } else {
    renderFeed('feed-home', dadosBase.filter(i=>i.tipo===tipoAtivo));
  }
}"""
    html = html.replace(match.group(0), nova_mudar)
    print("✅ mudarFeed corrigido (mix sem vagas)")

# 6.3 Função filtrarHome
padrao_filtrar = r'(function filtrarHome\(cat,btn\)\{)(.*?)(\n\})'
match = re.search(padrao_filtrar, html, re.DOTALL)
if match:
    nova_filtrar = """function filtrarHome(cat,btn){
  btn.parentElement.querySelectorAll('.btn-f').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  if(tipoAtivo==='noticia'){
    const base = cat==='Tudo'
      ? dadosBase.filter(i=>i.tipo!=='vaga')
      : dadosBase.filter(i=>i.tipo===tipoAtivo && i.categoria===cat);
    renderFeed('feed-home', base);
  } else {
    renderFeed('feed-home', dadosBase.filter(i=>i.tipo===tipoAtivo && (cat==='Tudo'||i.categoria===cat)));
  }
}"""
    html = html.replace(match.group(0), nova_filtrar)
    print("✅ filtrarHome corrigido")

# 6.4 Função actualizarFiltrosHome
padrao_actualizar = r'(function actualizarFiltrosHome\(\)\{)(.*?)(\n\})'
match = re.search(padrao_actualizar, html, re.DOTALL)
if match:
    nova_actualizar = """function actualizarFiltrosHome(){
  const el=document.getElementById('filtros-home');if(!el)return;
  const base = tipoAtivo==='noticia'
    ? dadosBase.filter(i=>i.tipo!=='vaga')
    : dadosBase.filter(i=>i.tipo===tipoAtivo);
  const cats=[...new Set(base.filter(i=>i.categoria).map(i=>i.categoria))];
  el.innerHTML=`<button class="btn-f active" onclick="filtrarHome('Tudo',this)">Tudo</button>`
    +cats.map(c=>`<button class="btn-f" onclick="filtrarHome('${c}',this)">${c}</button>`).join('');
}"""
    html = html.replace(match.group(0), nova_actualizar)
    print("✅ actualizarFiltrosHome corrigido")

# ============================================================
# 7. ESTILOS ADICIONAIS (art-lead, art-fonte, etc)
# ============================================================

if '.art-lead' not in html:
    estilos_art = """
.art-body p{margin-bottom:14px;line-height:1.8;}
.art-lead{font-size:15px;font-weight:600;border-left:3px solid var(--red);padding-left:14px;margin-bottom:18px;}
.art-fonte{display:flex;align-items:center;gap:6px;margin-top:16px;font-size:10px;text-transform:uppercase;color:var(--muted);border-top:1px solid var(--border-light);padding-top:12px;}
.art-fonte i{color:var(--red);}
"""
    if '</style>' in html:
        html = html.replace('</style>', estilos_art + '\n</style>')
        print("✅ Estilos art-lead adicionados")

# ============================================================
# 8. SALVAR E ENVIAR
# ============================================================

if html == original:
    print("\n⚠️ Nenhuma alteração foi feita.")
    print("   O patch completo já pode ter sido aplicado.")
    exit(0)

with open(FICHEIRO, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\n💾 {FICHEIRO} guardado")

print("\n🚀 A publicar no GitHub...")
for cmd in [
    ["git", "add", "index.html"],
    ["git", "commit", "-m", f"🎨 Patch completo — todas as melhorias — {datetime.now().strftime('%d/%m/%Y %H:%M')}"],
    ["git", "push"]
]:
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = r.returncode == 0 or "nothing to commit" in (r.stdout or r.stderr)
    print(f"  {'✅' if ok else '⚠️'} git {cmd[1]}")

print("\n" + "="*60)
print("🎉 PATCH COMPLETO APLICADO COM SUCESSO!")
print("")
print("✅ MELHORIAS APLICADAS:")
print("   1. Data visível em cada card")
print("   2. Imagens diferentes por categoria")
print("   3. Descrições formatadas em parágrafos")
print("   4. Primeira frase em destaque (lead)")
print("   5. Destaque com imagem de fundo")
print("   6. Filtro Tudo = notícias + boladas (sem vagas)")
print("")
print("🌐 Site: https://bycoast.github.io/nampula-e-a-cena/")
print("="*60)
