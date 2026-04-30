#!/usr/bin/env python3
import subprocess
from datetime import datetime

FICHEIRO = "index.html"

print("="*55)
print("📝 PATCH — Formatação de Descrições")
print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("="*55)

with open(FICHEIRO, 'r', encoding='utf-8') as f:
    html = f.read()

# CSS para formatação
CSS_NOVO = """
/* FORMATAÇÃO DE ARTIGOS */
.art-body{
  font-family:'Inter',sans-serif;
  font-size:14.5px;
  line-height:1.85;
  color:var(--txt2);
}
.art-body p{
  margin-bottom:16px;
  line-height:1.85;
}
.art-lead{
  font-size:15px;
  font-weight:600;
  color:var(--txt);
  border-left:3px solid #e53e3e;
  padding-left:14px;
  margin-bottom:18px;
}"""

# Adicionar CSS se não existir
if '.art-body' not in html:
    html = html.replace('</style>', CSS_NOVO + '\n</style>')
    print("✅ CSS adicionado")
else:
    print("✅ CSS já existe")

# Função formatarDesc simplificada
NOVA_FUNC = """
function formatarDesc(texto){
  if(!texto || texto.length < 10) return '<p>Clique para ler mais.</p>';
  texto = texto.replace(/\\s+/g, ' ').trim();
  var frases = texto.match(/[^.!?]+[.!?]+/g) || [texto];
  var pars = [];
  for(var i = 0; i < frases.length; i += 2){
    var grupo = frases[i];
    if(frases[i+1]) grupo += ' ' + frases[i+1];
    if(grupo.length > 15) pars.push(grupo);
  }
  if(pars.length === 0) return '<p>' + texto + '</p>';
  var h = '<p class="art-lead">' + pars[0] + '</p>';
  for(var i = 1; i < pars.length; i++){
    h += '<p>' + pars[i] + '</p>';
  }
  return h;
}
"""

# Substituir função antiga (simples replace)
if 'function formatarDesc' in html:
    linhas = html.split('\n')
    novo_html = []
    pular = False
    for linha in linhas:
        if 'function formatarDesc' in linha:
            novo_html.append(NOVA_FUNC)
            pular = True
        elif pular and linha.strip() == '}':
            pular = False
        elif not pular:
            novo_html.append(linha)
    html = '\n'.join(novo_html)
    print("✅ formatarDesc substituída")
else:
    # Inserir antes de buildCard
    html = html.replace('function buildCard', NOVA_FUNC + '\n\nfunction buildCard')
    print("✅ formatarDesc inserida")

# Garantir que usa formatarDesc
if '${item.desc}' in html:
    html = html.replace('${item.desc}', '${formatarDesc(item.desc)}')
    print("✅ buildCard actualizado")

# Salvar
with open(FICHEIRO, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\n💾 {FICHEIRO} guardado")

# Git push
print("\n🚀 Publicando...")
for cmd in [["git","add","index.html"], ["git","commit","-m","📝 Formatação de descrições"], ["git","push"]]:
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = r.returncode == 0 or "nothing to commit" in r.stderr
    print(f"  {'✅' if ok else '⚠️'} {' '.join(cmd[:2])}")

print("\n✅ PATCH APLICADO!")
