import pathlib,markdown,datetime,re,yaml,shutil
from jinja2 import Template
ROOT=pathlib.Path(__file__).resolve().parents[1]
DIST=ROOT/'dist';TPL=ROOT/'site/templates';ASSETS=ROOT/'site/assets';POSTS=ROOT/'content/posts'
def tpl(n):return Template((TPL/n).read_text(encoding='utf-8'))
def render(c,t,d=''):return tpl('base.html').render(content=c,title=t,description=d,year=datetime.datetime.now().year)
def build():
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir(); shutil.copytree(ASSETS,DIST,dirs_exist_ok=True)
    cards=[]
    for md in POSTS.glob('*.md'):
        raw=md.read_text(encoding='utf-8')
        meta=yaml.safe_load(re.findall(r'^---(.*?)---',raw,re.S)[0])
        body=re.sub(r'^---.*?---','',raw,flags=re.S).strip()
        html=markdown.markdown(body); slug=meta['slug']
        page=render(tpl('post.html').render(title=meta['title'],date=meta['date'],body=html),meta['title'])
        (DIST/f'{slug}.html').write_text(page,encoding='utf-8')
        cards.append(f"<div class='card'><h3><a href='{slug}.html'>{meta['title']}</a></h3><p>{meta['excerpt']}</p></div>")
    index=render(tpl('index.html').render(posts=''.join(cards)),'Início')
    (DIST/'index.html').write_text(index,encoding='utf-8')
if __name__=='__main__': build()