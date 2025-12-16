import json
import markdown
import pathlib
import datetime
from jinja2 import Template

ROOT = pathlib.Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "content" / "posts"
OUT_DIR = ROOT / "site" / "output"
TPL_DIR = ROOT / "site" / "templates"
CONFIG = ROOT / "config.json"

def load_config():
    if CONFIG.exists():
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    return {}

def load_template(name):
    return Template((TPL_DIR / name).read_text(encoding="utf-8"))

def render_page(content, title, description):
    base = load_template("base.html")
    return base.render(
        content=content,
        title=title,
        description=description,
        year=datetime.datetime.now().year
    )

def build_posts():
    posts = []

    for md in sorted(POSTS_DIR.glob("*.md")):
        raw = md.read_text(encoding="utf-8")

        import re, yaml
        meta_raw = re.findall(r"^---(.*?)---", raw, re.S)[0]
        body_md = re.sub(r"^---(.*?)---", "", raw, flags=re.S).strip()

        meta = yaml.safe_load(meta_raw)
        html_body = markdown.markdown(body_md, extensions=["fenced_code", "toc"])

        slug = meta.get("slug", md.stem)

        html = render_page(
            load_template("post.html").render(
                title=meta["title"],
                date=meta["date"],
                tags=", ".join(meta.get("tags", [])),
                body=html_body
            ),
            meta["title"],
            meta.get("excerpt", "")
        )

        (OUT_DIR / f"{slug}.html").write_text(html, encoding="utf-8")

        posts.append({
            "title": meta["title"],
            "excerpt": meta.get("excerpt", ""),
            "slug": slug,
            "date": meta["date"]
        })

    return posts

def build_index(posts):
    cards = []

    for p in sorted(posts, key=lambda x: x["date"], reverse=True):
        cards.append(
            f"<article class='post-card'>"
            f"<h3><a href='{p['slug']}.html'>{p['title']}</a></h3>"
            f"<p>{p['excerpt']}</p>"
            f"<div class='meta'>{p['date']}</div>"
            f"</article>"
        )

    inner = load_template("index.html").render(posts="\n".join(cards))

    html = render_page(
        inner,
        "Início",
        "Conteúdo diário sobre finanças e investimentos"
    )

    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")

def build_extras(posts):
    base = load_config().get(
        "domain",
        "https://santiiagoleandro-ops.github.io/site-financas-llama"
    )

    # robots.txt
    (OUT_DIR / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml",
        encoding="utf-8"
    )

    # sitemap.xml
    sitemap = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f"<url><loc>{base}/</loc></url>"
    ]

    for p in posts:
        sitemap.append(f"<url><loc>{base}/{p['slug']}.html</loc></url>")

    sitemap.append("</urlset>")

    (OUT_DIR / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    posts = build_posts()
    build_index(posts)
    build_extras(posts)
    print("Site gerado com sucesso:", len(posts), "posts")

if __name__ == "__main__":
    main()
