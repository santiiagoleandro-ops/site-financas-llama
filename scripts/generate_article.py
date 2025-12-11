# Gera artigos usando HuggingFace Inference API with LLaMA 3.1 as MANDATORY engine.
import os
import json
import argparse
from datetime import datetime
import re
import logging
import requests

logging.basicConfig(level=logging.INFO, filename='generation.log', filemode='a', format='%(asctime)s %(levelname)s:%(message)s')

HF_MODEL = None

def load_file(p):
    with open(p,'r',encoding='utf8') as f:
        return f.read()

def safe_slug(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9\-\_\s]', '', s)
    s = re.sub(r'\s+', '-', s).strip('-')
    return s[:60]

def call_hf_inference(prompt_text):
    # Use HuggingFace Inference API. HUGGINGFACE_API_KEY MUST be set.
    hf_key = os.environ.get('HUGGINGFACE_API_KEY')
    if not hf_key:
        raise Exception('HUGGINGFACE_API_KEY obrigatória; gere uma chave gratuita em https://huggingface.co/settings/tokens')
    cfg = {}
    try:
        with open('config.json','r',encoding='utf8') as f:
            cfg = json.load(f)
    except:
        pass
    model = cfg.get('huggingface_model','meta-llama/Llama-3.1-8B-Instruct')
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {hf_key}"}
    payload = {"inputs": prompt_text, "options": {"wait_for_model": True, "use_cache": False}}
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    if r.status_code != 200:
        raise Exception(f'HF Inference API error {r.status_code}: {r.text}')
    out = r.json()
    # Try to extract text in common hf formats
    if isinstance(out, dict) and out.get('error'):
        raise Exception('HF error: ' + out.get('error'))
    if isinstance(out, list):
        # many models return a list of strings or dicts
        first = out[0]
        if isinstance(first, dict) and 'generated_text' in first:
            return first['generated_text']
        if isinstance(first, dict) and 'text' in first:
            return first['text']
        if isinstance(first, str):
            return first
    if isinstance(out, dict) and 'generated_text' in out:
        return out['generated_text']
    # fallback to stringify
    return str(out)

def templated_generator(mode, payload, topics):
    # conservative templated generator if HF temporarily unavailable (not primary)
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
    if mode == 'trending':
        title_topic = payload.get('TRENDS')[0] if payload.get('TRENDS') else (payload.get('NEWS')[0]['title'] if payload.get('NEWS') else 'Notícias do dia')
        title = f"{title_topic} — O que investidores precisam saber hoje"
        excerpt = f"Resumo sobre {title_topic} e seus possíveis impactos no mercado."
        facts = payload.get('FACTS') or payload.get('NEWS') or []
        bullets = []
        for f in facts[:5]:
            if isinstance(f, dict):
                t = f.get('title') or f.get('summary') or str(f)
                u = f.get('url','')
                bullets.append(f"- {t} {'('+u+')' if u else ''}")
            else:
                bullets.append(f"- {str(f)}")
        body = []
        body.append("## Contexto")
        body.append(f"O tema em destaque é **{title_topic}**. Abaixo listamos fatos coletados automaticamente das fontes disponíveis.")
        body.append("## Desenvolvimento")
        for b in bullets:
            body.append(b)
        body.append("## Impacto para o investidor")
        body.append("Com base nos fatos acima, investidores devem considerar o horizonte de investimento e a tolerância ao risco; reavalie alocação se necessário.")
        body.append("## Conclusão")
        body.append("Acompanhe as fontes citadas para mais detalhes.")
        body_text = "\n\n".join(body)
        md = f"""---
title: "{title}"
date: "{now}"
tags: ["finanças","trending"]
excerpt: "{excerpt}"
slug: "{safe_slug(title)}"
type: "trending"
---

# {title}

{excerpt}

{body_text}

## Fontes consultadas
"""
        for n in (payload.get('NEWS') or [])[:10]:
            if isinstance(n, dict) and n.get('url'):
                md += f"- [{n.get('title','notícia')}]({n.get('url')})\n"
        return md
    topic = topics[0] if topics else 'Finanças básicas'
    title = f"{topic} — Guia rápido"
    excerpt = f"Guia prático sobre {topic}."
    body = []
    body.append("## Contexto")
    body.append(f"Este artigo aborda **{topic}**, apresentando noções práticas para investidores.")
    body.append("## Desenvolvimento")
    body.append("1. Defina horizonte de investimento.")
    body.append("2. Diversifique entre renda fixa, renda variável e ativos alternativos.")
    body.append("3. Rebalanceie periodicamente e controle custos.")
    body.append("## Impacto para o investidor")
    body.append("Essas práticas ajudam a reduzir riscos e melhorar retorno no longo prazo.")
    body.append("## Conclusão")
    body.append("Consistência e disciplina são fundamentais.")
    body_text = "\n\n".join(body)
    md = f"""---
title: "{title}"
date: "{now}"
tags: ["finanças","nicho"]
excerpt: "{excerpt}"
slug: "{safe_slug(title)}"
type: "nicho"
---

# {title}

{excerpt}

{body_text}
"""
    return md

def inject_monetization(markdown_text, affiliate_map):
    lines = []
    lines.append('\n---\n')
    lines.append('### Recomendações e parceiros\n')
    for name, url in affiliate_map.items():
        lines.append(f'- [{name}]({url})\n')
    lines.append('\n*Links acima podem conter programas de afiliados.*\n')
    return markdown_text + '\n' + '\n'.join(lines)

def main(count=1):
    trending = {}
    if os.path.exists('trending_data.json'):
        with open('trending_data.json','r',encoding='utf8') as f:
            trending = json.load(f)
    with open('TOPICOS_NICHO.json','r',encoding='utf8') as f:
        topics = json.load(f)
    prompt_template = load_file('prompt_financas.txt')
    with open('AFFILIATE_MAP.json','r',encoding='utf8') as f:
        affiliate_map = json.load(f)

    for i in range(count):
        mode = 'trending' if (trending.get('news') or trending.get('trends')) else 'nicho'
        payload = {
            'TRENDS': trending.get('trends',[]),
            'NEWS': trending.get('news',[]),
            'REDDIT': trending.get('reddit',[]),
            'FACTS': trending.get('news',[]),
            'NICHO': 'finanças e investimentos'
        }
        prompt_full = prompt_template + "\n\n" + json.dumps(payload, ensure_ascii=False, indent=2)
        logging.info(f'Gerando post {i+1} modo={mode} via HuggingFace')
        md = None
        try:
            md = call_hf_inference(prompt_full)
        except Exception as e:
            logging.exception('HF Inference failed; fallback to template')
            md = templated_generator(mode, payload, topics)
        # ensure markdown has frontmatter; if HF returned raw text, accept it if valid, else wrap
        if not md.strip().startswith('---'):
            # attempt to wrap into minimal frontmatter
            title = f"Artigo automático {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
            md = f"""---
title: "{title}"
date: "{now}"
tags: ["finanças"]
excerpt: "Artigo gerado automaticamente"
slug: "{safe_slug(title)}"
type: "nicho"
---

# {title}

{md}
"""
        md = inject_monetization(md, affiliate_map)
        dt = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        m = re.search(r'^title:\s*"(.+)"', md, flags=re.MULTILINE)
        title = m.group(1) if m else f'auto-post-{dt}'
        slug = safe_slug(title)
        out_path = os.path.join('content', 'posts')
        os.makedirs(out_path, exist_ok=True)
        fname = f"{slug}.md"
        with open(os.path.join(out_path, fname), 'w', encoding='utf8') as f:
            f.write(md)
        logging.info('Post salvo em %s', os.path.join(out_path, fname))
        print('Post salvo em', os.path.join(out_path, fname))

if __name__ == '__main__':
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=1)
    args = parser.parse_args()
    main(count=args.count)
