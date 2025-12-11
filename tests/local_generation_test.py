import os, subprocess, json

def run_collect():
    r = subprocess.run(['python','scripts/collect_trending.py'], capture_output=True, text=True)
    print('collect_trending:', r.returncode)
    print(r.stdout)
    print(r.stderr)

def run_generate():
    # requires HUGGINGFACE_API_KEY in env
    r = subprocess.run(['python','scripts/generate_article.py','--count','1'], capture_output=True, text=True)
    print('generate_article:', r.returncode)
    print(r.stdout)
    print(r.stderr)

if __name__ == '__main__':
    print('Running local generation test (collect + generate)')
    run_collect()
    run_generate()
    print('Check content/posts/ for generated markdown and site/output after running site_generator.py')
