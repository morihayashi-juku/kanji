"""漢字データ（g1.txt〜g3.txt）を読み込んで検証し、JSONにする。"""
import json, re, sys, os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
TOKEN = re.compile(r'\{([^{}|]+)\|([^{}|]+)(?:\|([^{}|]*))?\}|\[([^\[\]|]+)\|([^\[\]|]+)\]')
CJK = re.compile(r'[一-鿿々]')

def kata2hira(s):
    return ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s)

def parse_sentence(raw):
    """文を部品の配列にする。 t: text / w: ふつうの漢字語 / q: 出題する語"""
    parts, pos, nq = [], 0, 0
    for m in TOKEN.finditer(raw):
        if m.start() > pos:
            parts.append({'t': raw[pos:m.start()]})
        if m.group(1):
            parts.append({'q': m.group(1), 'r': m.group(2), 'o': m.group(3) or ''})
            nq += 1
        else:
            parts.append({'w': m.group(4), 'r': m.group(5)})
        pos = m.end()
    if pos < len(raw):
        parts.append({'t': raw[pos:]})
    errs = []
    if nq != 1:
        errs.append(f'出題語が{nq}個')
    for p in parts:
        if 't' in p and (CJK.search(p['t']) or re.search(r'[\[\]{}|]', p['t'])):
            errs.append(f'記号か漢字がはみ出し: {p["t"]}')
        if 'w' in p and len(p['r']) < 1:
            errs.append('読みなし')
    return parts, errs

def load():
    grades, errors = [], []
    for g in (1, 2, 3):
        path = os.path.join(DATA, f'g{g}.txt')
        units, cur, item = [], None, None
        for ln, line in enumerate(open(path, encoding='utf-8'), 1):
            line = line.rstrip('\n')
            if not line.strip() or line.startswith('#') or line.startswith('G '):
                continue
            tag, rest = line[:2], line[2:].strip()
            if tag == 'U ':
                title, pages = rest.split('|')
                cur = {'title': title, 'pages': pages, 'items': []}
                units.append(cur)
            elif tag in ('K ', 'Y ', 'T '):
                word, yomi = rest.split('|')
                item = {'type': tag[0], 'word': word, 'yomi': yomi, 'ex': []}
                cur['items'].append(item)
            elif tag == '- ':
                parts, errs = parse_sentence(rest)
                for e in errs:
                    errors.append(f'g{g}:{ln} {e}: {rest}')
                item['ex'].append(parts)
            else:
                errors.append(f'g{g}:{ln} 読めない行: {line}')
        grades.append(units)
    return grades, errors

def validate(grades):
    errors, warns = [], []
    learned_at = {}  # 漢字 -> (学年, 単元番号)
    for gi, units in enumerate(grades):
        for ui, u in enumerate(units):
            for it in u['items']:
                if it['type'] == 'K':
                    if it['word'] in learned_at:
                        errors.append(f'重複: {it["word"]}')
                    learned_at[it['word']] = (gi, ui)
    for gi, units in enumerate(grades):
        for ui, u in enumerate(units):
            for it in u['items']:
                if not it['ex']:
                    errors.append(f'例文なし: 小{gi+1} {u["title"]} {it["word"]}')
                usable = 0
                for ex in it['ex']:
                    q = next(p for p in ex if 'q' in p)
                    txt = ''.join(p.get('t', '') + p.get('w', '') + p.get('q', '') + p.get('o', '') for p in ex)
                    if it['type'] == 'K' and it['word'] not in q['q']:
                        errors.append(f'出題語に{it["word"]}がない: {txt}')
                    if it['type'] in 'YT':
                        ks = CJK.findall(it['word'])
                        if not all(k in q['q'] for k in ks):
                            warns.append(f'見出しの漢字が出題語にない: {it["word"]} / {txt}')
                    late = [c for c in CJK.findall(q['q']) if learned_at.get(c, (9, 0)) > (gi, ui)]
                    if late:
                        warns.append(f'あとで習う漢字が出題語に（その単元では使わない）: 小{gi+1}「{u["title"]}」{it["word"]}: {txt} ← {"".join(late)}')
                    else:
                        usable += 1
                    if it['type'] == 'K' and len(q['q']) == 1:
                        yomis = [kata2hira(y) for y in it['yomi'].split('・')]
                        full = q['r'] + q['o']
                        if not any(full.startswith(y[:len(q['r'])]) and (y.startswith(q['r']) or q['r'].startswith(y[:-1])) for y in yomis):
                            warns.append(f'読みの確認: {it["word"]}={q["r"]}（{it["yomi"]}）: {txt}')
                if usable == 0:
                    errors.append(f'その単元で使える例文がない: 小{gi+1} {u["title"]} {it["word"]}')
    return learned_at, errors, warns

if __name__ == '__main__':
    grades, errors = load()
    learned_at, e2, warns = validate(grades)
    errors += e2
    counts = [sum(1 for u in us for it in u['items'] if it['type'] == 'K') for us in grades]
    print('漢字数', counts)
    print('例文数', sum(len(it['ex']) for us in grades for u in us for it in u['items']))
    for e in errors: print('ERROR', e)
    for w in warns: print('WARN', w)
    out = [{'grade': g + 1, 'units': us} for g, us in enumerate(grades)]
    json.dump(out, open(os.path.join(DATA, 'kanji_data.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
