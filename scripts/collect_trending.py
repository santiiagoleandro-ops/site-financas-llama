# Coleta tendências: Google Trends (pytrends), GDELT news e Reddit (via JSON público)
import json
import requests
from pytrends.request import TrendReq

def get_trends():
    try:
        pytrends = TrendReq(hl='pt-BR', tz=180)
        kw_list = ['investimentos','inflação','selic','ações','mercado']
        pytrends.build_payload(kw_list, timeframe='now 1-d')
        related = pytrends.related_queries()
        keywords = []
        for k in related:
            v = related[k].get('top')
            if v is not None:
                keywords += v['query'].head(3).tolist()
        return list(dict.fromkeys(keywords))[:10]
    except Exception as e:
        print('pytrends error', e)
        return []

def get_gdelt_news():
    try:
        url = 'https://api.gdeltproject.org/api/v2/doc/doc?query=finance%20OR%20investing&format=json'
        r = requests.get(url, timeout=15).json()
        docs = r.get('articles', [])
        news = []
        for d in docs[:15]:
            news.append({
                'title': d.get('title'),
                'summary': d.get('segs') if d.get('segs') else '',
                'url': d.get('url'),
                'date': d.get('seendate')
            })
        return news
    except Exception as e:
        print('gdelt error', e)
        return []

def get_reddit():
    try:
        url = 'https://www.reddit.com/r/investing/top.json?t=day&limit=8'
        r = requests.get(url, headers={'User-agent':'Mozilla/5.0'}, timeout=10)
        items = r.json().get('data',{}).get('children',[])
        return [{'title': i['data']['title'], 'url': 'https://reddit.com'+i['data']['permalink']} for i in items]
    except Exception as e:
        print('reddit error', e)
        return []

def save():
    data = {
        'trends': get_trends(),
        'news': get_gdelt_news(),
        'reddit': get_reddit()
    }
    with open('trending_data.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('trending_data.json salvo')

if __name__ == '__main__':
    save()
