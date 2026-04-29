#!/usr/bin/env python3
"""
patch_cards.py — Corrige data visível + imagens por categoria
Corre no Termux:
  cd /data/data/com.termux/files/home/nampula-e-a-cena
  python patch_cards.py
"""
import subprocess
from datetime import datetime

FICHEIRO = "index.html"

print("="*55)
print("🎨 PATCH CARDS — Data + Imagens por Categoria")
print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("="*55)

with open(FICHEIRO, 'r', encoding='utf-8') as f:
    html = f.read()

original = html

# ════════════════════════════════════════════════════════════
# 1. ADICIONAR IMAGENS POR CATEGORIA + buildCard CORRIGIDO
# ════════════════════════════════════════════════════════════

NOVO_BUILDCARD = """
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
  'default':       'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&q=70'
};

function imgFallback(item){
  return IMG_CAT[item.categoria] || IMG_CAT['default'];
}

// BUILD CARD
function buildCard(item,i){
  const cls=item.tipo==='vaga'?'item-vaga':item.tipo==='bolada'?'item-bolada':'';
  const cat=item.categoria||item.tipo;
  const fallback=imgFallback(item);
  const data=item.data||'';
  const thumb=item.video
    ?`<div class="c-thumb" style="display:flex;align-items:center;justify-content:center;background:#0d0d0d;"><i class="fas fa-play-circle" style="font-size:48px;color:rgba(255,255,255,.45);"></i><span class="c-tag">${cat}</span></div>`
    :`<div class="c-thumb"><img src="${item.img||fallback}" loading="lazy" onerror="this.src='${fallback}'"><span class="c-tag">${cat}</span>${data?`<span class="c-date-overlay"><i class="fas fa-calendar-alt" style="font-size:8px;margin-right:4px;"></i>${data}</span>`:''}</div>`;
  const body=item.video?`<video controls style="width:100%;margin-bottom:14px;"><source src="${item.video}" type="video/mp4"></video>`:'';
  return`<article class="card ${cls}" style="animation-delay:${i*.07}s" itemscope itemtype="https://schema.org/Article">
    <div onclick="toggleAc(this)" class="faq-header">
      ${thumb}
      <div class="c-body">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:7px;">
          <span class="c-cat">${cat}</span>
          ${data?`<time class="c-time" itemprop="datePublished" style="font-size:10px;color:var(--muted);font-family:'Outfit',sans-serif;"><i class="fas fa-clock" style="font-size:9px;margin-right:3px;"></i>${data}</time>`:''}
        </div>
        <h3 class="c-title" itemprop="headline">${item.titulo}</h3>
        <div class="c-footer">
          <span class="c-read">Ler mais <i class="fas fa-chevron-down exp-ic" style="font-size:9px;transition:.3s;"></i></span>
        </div>
      </div>
    </div>
    <div class="faq-content">
      <div class="faq-body">
        ${body}
        <p class="art-body" itemprop="articleBody">${item.desc}</p>
        ${item.link_vaga?`<a href="${item.link_vaga}" target="_blank" class="btn-apply"><i class="fas fa-bolt"></i> Candidatar Agora</a>`:''}
        <a href="https://wa.me/?text=*${encodeURIComponent('Vê isto no Nampula é a Cena:')}* ${encodeURIComponent(item.titulo)}" target="_blank" class="btn-share"><i class="fab fa-whatsapp"></i> Partilhar</a>
      </div>
    </div>
  </article>`;
}"""

# Localizar e substituir o bloco buildCard existente
import re

# Remove qualquer bloco IMG_CAT anterior se existir
html = re.sub(
    r'// IMAGENS FALLBACK POR CATEGORIA.*?(?=function renderFeed)',
    '',
    html,
    flags=re.DOTALL
)

# Substituir função buildCard
html = re.sub(
    r'// BUILD CARD\s*\nfunction buildCard\(item,i\)\{.*?\n\}',
    NOVO_BUILDCARD,
    html,
    flags=re.DOTALL
)

if html == original:
    print("⚠️  buildCard não encontrado pelo padrão principal.")
    print("   A tentar método alternativo...")
    # Tentar inserir antes de renderFeed
    if 'function renderFeed' in html:
        html = html.replace(
            'function renderFeed',
            NOVO_BUILDCARD + '\n\nfunction renderFeed'
        )
        print("✅ Inserido antes de renderFeed")
    else:
        print("❌ Não foi possível localizar ponto de inserção.")
        exit(1)
else:
    print("✅ buildCard substituído com sucesso")

# ════════════════════════════════════════════════════════════
# 2. GUARDAR
# ════════════════════════════════════════════════════════════
if html == original:
    print("\n⚠️  Nenhuma alteração aplicada. Verifica o ficheiro.")
    exit(0)

with open(FICHEIRO, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"💾 {FICHEIRO} guardado")

# ════════════════════════════════════════════════════════════
# 3. GIT PUSH
# ════════════════════════════════════════════════════════════
print("\n🚀 A publicar no GitHub...")
for cmd in [
    ["git", "add", "index.html"],
    ["git", "commit", "-m", f"🎨 Cards: data visível + imagens por categoria — {datetime.now().strftime('%d/%m/%Y %H:%M')}"],
    ["git", "push"]
]:
    r = subprocess.run(cmd, capture_output=True, text=True)
    saida = r.stdout.strip() or r.stderr.strip()
    ok = r.returncode == 0 or "nothing to commit" in saida
    print(f"  {'✅' if ok else '⚠️ '} {' '.join(cmd[:2])}: {saida[:80] if not ok else ''}")

print("\n" + "="*55)
print("🎉 SITE ACTUALIZADO!")
print("   ✅ Data visível em todos os cards")
print("   ✅ Imagens diferentes por categoria")
print("="*55)
