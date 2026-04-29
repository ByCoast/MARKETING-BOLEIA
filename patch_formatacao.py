import re
import subprocess
from datetime import datetime

FICHEIRO = "index.html"

print("="*55)
print("📝 PATCH DE FORMATAÇÃO — Nampula é a Cena")
print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("="*55)

with open(FICHEIRO, 'r', encoding='utf-8') as f:
    html = f.read()

original = html

# 1. MELHORAR CSS DO CORPO DO ARTIGO
old_art_body = re.search(r'\.art-body\{[^}]+\}', html)
if old_art_body:
    html = html.replace(old_art_body.group(), 
    '.art-body{font-family:\'Inter\',sans-serif;font-size:15px;'
    'line-height:1.9;color:var(--txt2);white-space:normal;'
    'text-align:left;word-break:break-word;}')
    print("✅ CSS art-body actualizado")

# Adicionar estilos extras
estilos_extras = """
.art-body p{margin-bottom:14px;line-height:1.9;}
.art-body p:last-child{margin-bottom:0;}
.art-body .art-lead{font-size:16px;font-weight:600;color:var(--txt);
  border-left:3px solid var(--red);padding-left:14px;
  margin-bottom:18px;line-height:1.7;}
.art-fonte{display:inline-flex;align-items:center;gap:6px;
  margin-top:16px;font-family:'Outfit',sans-serif;
  font-size:10px;font-weight:700;letter-spacing:2px;
  text-transform:uppercase;color:var(--muted);
  border-top:1px solid var(--border-light);
  padding-top:12px;width:100%;}
.art-fonte i{color:var(--red);}"""

html = html.replace('</style>', estilos_extras + '\n</style>', 1)
print("✅ Estilos de parágrafos adicionados")

# 2. SUBSTITUIR A LINHA DO ART-BODY
old_line = '        <p class="art-body" itemprop="articleBody">${item.desc}</p>'
new_line = '        <div class="art-body" itemprop="articleBody">${formatarDesc(item.desc)}</div>\n        ${item.fonte?`<span class="art-fonte"><i class="fas fa-link"></i> Fonte: ${item.fonte}</span>`:""}'

if old_line in html:
    html = html.replace(old_line, new_line)
    print("✅ BuildCard actualizado")
else:
    html = re.sub(
        r'<p class="art-body"[^>]*>\$\{item\.desc\}</p>',
        '<div class="art-body" itemprop="articleBody">${formatarDesc(item.desc)}</div>\n        ${item.fonte?`<span class="art-fonte"><i class="fas fa-link"></i> Fonte: ${item.fonte}</span>`:""}',
        html
    )
    print("✅ BuildCard actualizado (alternativa)")

# 3. ADICIONAR FUNÇÃO formatarDesc
funcao = """
// ══ FORMATAR DESCRIÇÃO ══
function formatarDesc(texto){
  if(!texto || texto.length < 10) return '<p>Clique para ler mais.</p>';
  texto = texto.replace(/\\s+/g,' ').trim();
  texto = texto.replace(/\\.\\.\\./g,'…');
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
    if(p.trim().length > 10)
      html += `<p>${p.trim()}</p>`;
  });
  return html || `<p>${texto}</p>`;
}
"""

if 'function buildCard' in html:
    html = html.replace('function buildCard', funcao + '\nfunction buildCard')
    print("✅ Função formatarDesc adicionada")
else:
    html = html.replace('async function carregar', funcao + '\nasync function carregar')
    print("✅ Função formatarDesc adicionada (alternativa)")

# 4. MELHORAR DESCRIÇÃO DO DESTAQUE
old_desc = "document.getElementById('destaque-desc').textContent=(item.desc||'').substring(0,160)+'...';"
new_desc = """const frasesDest=(item.desc||'').match(/[^.!?]+[.!?]+/g)||[];
  const resumo=frasesDest.slice(0,2).join(' ').trim()||((item.desc||'').substring(0,160));
  document.getElementById('destaque-desc').textContent=resumo;"""

if old_desc in html:
    html = html.replace(old_desc, new_desc)
    print("✅ Descrição do destaque melhorada")

if html == original:
    print("\n⚠️ Nenhuma alteração detectada.")
    exit(0)

with open(FICHEIRO, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\n💾 {FICHEIRO} guardado")

print("\n🚀 A publicar no GitHub...")
cmds = [
    ["git", "add", "index.html"],
    ["git", "commit", "-m", "📝 Formatação automática de artigos"],
    ["git", "push"]
]
for cmd in cmds:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 or "nothing to commit" in result.stdout:
        print(f"  ✅ {' '.join(cmd)}")
    else:
        print(f"  ⚠️ {result.stderr[:100]}")

print("\n" + "="*55)
print("🎉 FORMATAÇÃO ACTUALIZADA!")
print("="*55)
