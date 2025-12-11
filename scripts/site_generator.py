import os, json, markdown, pathlib, datetime
from jinja2 import Template

ROOT = pathlib.Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "content/posts"
OUT_DIR = ROOT / "site/output"
TPL_DIR = ROOT / "site/templates"
CONFIG = ROOT / "config.json"

def load_config():
    if CONFIG.exists():
        return json.loads(CONFIG.read_text(encoding='utf8'))
    return {}

def load_template(name):
    with open(TPL_DIR / name, "r", encoding="utf8") as f:
        return Template(f.read())

def render_page(template, **kwargs):
    base = load_template("base.html")
    inner = template.render(**kwargs)
    cfg = load_config()
    cf_token = cfg.get("cloudflare_beacon_token", "")
    ga_id = cfg.get("google_analytics_id", "")
    return base.render(content=inner, year=datetime.datetime.now().year, cf_token=cf_token, ga_id=ga_id, **kwargs)

def build_posts():
    posts = []
    for file in sorted(POSTS_DIR.glob("*.md")):
        text = file.read_text(encoding="utf8")
        import re, yaml
        fm = re.findall(r'^---(.*?)---', text, re.S | re.M)
        body_md = re.sub(r'^---(.*?)---', '', text, 1, flags=re.S|re.M).strip()
        meta = yaml.safe_load(fm[0])
        html_body = markdown.markdown(body_md, extensions=['fenced_code'])
        out_name = meta["slug"] + ".html"
        html = render_page(
            load_template("post.html"),
            title=meta["title"],
            description=meta.get("excerpt",""),
            date=meta["date"],
            tags=", ".join(meta.get("tags",[])),
            body=html_body
        )
        (OUT_DIR / out_name).write_text(html, encoding="utf8")
        posts.append({
            "title": meta["title"],
            "excerpt": meta.get("excerpt",""),
            "slug": meta["slug"],
            "date": meta["date"]
        })
    return posts

def build_index(posts):
    idx_tpl = load_template("index.html")
    list_items = []
    for p in sorted(posts, key=lambda x: x["date"], reverse=True):
        list_items.append(f"<article><h2><a href='/{p['slug']}.html'>{p['title']}</a></h2><p>{p['excerpt']}</p></article>")
    html = render_page(idx_tpl, title="Início", description="Site de finanças e investimentos", posts="\n".join(list_items))
    (OUT_DIR / "index.html").write_text(html, encoding="utf8")

def build_sitemap(posts):
    cfg = load_config()
    base = cfg.get("domain", "https://SEU_DOMINIO_AQUI")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines.append(f"<url><loc>{base}/index.html</loc></url>")
    for p in posts:
        lines.append(f"<url><loc>{base}/{p['slug']}.html</loc></url>")
    lines.append("</urlset>")
    (OUT_DIR / "sitemap.xml").write_text("\n".join(lines), encoding="utf8")

def build_rss(posts):
    cfg = load_config()
    base = cfg.get("domain", "https://SEU_DOMINIO_AQUI")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>','<rss version="2.0"><channel>']
    lines.append("<title>Finanças & Investimentos</title>")
    lines.append(f"<link>{base}</link>")
    lines.append("<description>Feed automático</description>")
    for p in posts[:20]:
        lines.append("<item>")
        lines.append(f"<title>{p['title']}</title>")
        lines.append(f"<link>{base}/{p['slug']}.html</link>")
        lines.append("</item>")
    lines.append("</channel></rss>")
    (OUT_DIR / "rss.xml").write_text("\n".join(lines), encoding="utf8")

def build_robots():
    cfg = load_config()
    base = cfg.get("domain", "https://SEU_DOMINIO_AQUI")
    text = f"""User-agent: *
Allow: /

Sitemap: {base}/sitemap.xml
"""
    (OUT_DIR / "robots.txt").write_text(text.strip(), encoding="utf8")

def main():
    OUT_DIR.mkdir(exist_ok=True)
    posts = build_posts()
    build_index(posts)
    build_sitemap(posts)
    build_rss(posts)
    build_robots()
    print("Site gerado com sucesso. Páginas:", len(posts))

if __name__ == "__main__":
    main()
