import pathlib
import shutil
import datetime
import re
import yaml
import markdown
from jinja2 import Template

ROOT = pathlib.Path(__file__).resolve().parents[1]

DIST = ROOT / "dist"
TEMPLATES = ROOT / "site/templates"
ASSETS = ROOT / "site/assets"
POSTS = ROOT / "content/posts"

def load_template(name):
    return Template((TEMPLATES / name).read_text(encoding="utf-8"))

def render_page(content, title, description=""):
    base = load_template("base.html")
    return base.render(
        content=content,
        title=title,
        description=description,
        year=datetime.datetime.now().year
    )

def build():
    # Limpa dist
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    # Copia assets
    shutil.copytree(ASSETS, DIST, dirs_exist_ok=True)

    post_template = load_template("post.html")
    index_template = load_template("index.html")

    cards = []

    for md_file in sorted(POSTS.glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")

        fm = re.search(r"^---(.*?)---", raw, re.S)
        if not fm:
            print(f"⚠️ Front-matter ausente em {md_file.name}, ignorado")
            continue

        meta = yaml.safe_load(fm.group(1)) or {}

        body_md = raw[fm.end():].strip()
        body_html = markdown.markdown(body_md, extensions=["extra"])

        title = meta.get("title", "Sem título")
        slug = meta.get("slug", md_file.stem)
        date = meta.get("date", "")
        excerpt = meta.get("excerpt", "")

        post_html = post_template.render(
            title=title,
            date=date,
            body=body_html
        )

        full_page = render_page(
            post_html,
            title,
            description=excerpt
        )

        (DIST / f"{slug}.html").write_text(full_page, encoding="utf-8")

        cards.append(
            f"""
            <div class="card">
              <h3><a href="{slug}.html">{title}</a></h3>
              <p>{excerpt}</p>
            </div>
            """
        )

    index_html = index_template.render(posts="".join(cards))
    index_page = render_page(
        index_html,
        "Bolso no Azul",
        "Clareza financeira para o dia a dia"
    )

    (DIST / "index.html").write_text(index_page, encoding="utf-8")

if __name__ == "__main__":
    build()
