"""data/g*.txt → index.html を作る。  使い方: python3 tools/build.py"""
import subprocess, sys, os
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, '..')
r = subprocess.run([sys.executable, os.path.join(here, 'parse.py')], capture_output=True, text=True)
print(r.stdout)
if r.returncode or 'ERROR' in r.stdout:
    sys.exit('データにエラーがあります。直してからもう一度。')
data = open(os.path.join(root, 'data', 'kanji_data.json'), encoding='utf-8').read()
html = open(os.path.join(here, 'template.html'), encoding='utf-8').read().replace('__DATA__', data)
open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(html)
print('index.html を作りました', len(html), 'bytes')
