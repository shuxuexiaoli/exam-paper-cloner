# -*- coding: utf-8 -*-
"""按段落索引克隆试卷：以模板 docx 为底，替换指定段落内容，公式写为 $...$。

用法:
  python gen_exam_parallel.py --src 模板.docx --dst 新卷.docx --content content.json

content.json 结构（键=段落索引，来自 inventory.py）:
  {"69": [["t","函数"],["m","y=\\ln(3-x)"],["t","的定义域为"],["b","          "],["t","。"]]}
片段类型: t=文本, m=LaTeX公式(自动包 $...$), b=下划线空格(答题空位)。
"""
import argparse
import json
import shutil
import zipfile
from copy import deepcopy
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
XML = '{http://www.w3.org/XML/1998/namespace}'


class Args:
    src = None
    dst = None
    content = None


def template_rpr(p):
    for r in p.findall(W + 'r'):
        rpr = r.find(W + 'rPr')
        if rpr is not None and r.find(W + 't') is not None:
            return rpr
    for r in p.findall(W + 'r'):
        rpr = r.find(W + 'rPr')
        if rpr is not None:
            return rpr
    return None


def make_run(kind, text, rpr):
    r = etree.Element(W + 'r')
    if rpr is not None:
        r.append(deepcopy(rpr))
    if kind == 'b':  # 下划线空格，还原答题空位
        rp = r.find(W + 'rPr')
        if rp is None:
            rp = etree.SubElement(r, W + 'rPr')
        for u in rp.findall(W + 'u'):
            rp.remove(u)
        u = etree.SubElement(rp, W + 'u')
        u.set(W + 'val', 'single')
    t = etree.SubElement(r, W + 't')
    t.set(XML + 'space', 'preserve')
    t.text = text
    return r


def set_para(p, segs):
    for seg in segs:
        if not (isinstance(seg, (list, tuple)) and len(seg) == 2
                and seg[0] in ('t', 'm', 'b')):
            raise SystemExit(
                '片段格式错误: %r\n应为 [kind, value] 二元列表，'
                'kind 为 "t"(文本) / "m"(LaTeX) / "b"(下划线空位)。' % (seg,))
    rpr = template_rpr(p)
    for ch in list(p):
        if ch.tag != W + 'pPr':          # 保留 pPr(含 numPr 自动编号)
            p.remove(ch)
    for kind, val in segs:
        if kind == 'm':
            p.append(make_run('t', '$%s$' % val, rpr))
        elif kind == 'b':
            p.append(make_run('b', val, rpr))
        else:
            p.append(make_run('t', val, rpr))


def main(a):
    assert a.content, '--content 必填'
    with open(a.content, encoding='utf-8-sig') as f:
        content = json.load(f)
    shutil.copy2(a.src, a.dst)
    with zipfile.ZipFile(a.src) as zin:
        items = {i.filename: zin.read(i.filename) for i in zin.infolist()}
    root = etree.fromstring(items['word/document.xml'])
    ps = list(root.iter(W + 'p'))
    print('total paras:', len(ps))
    pairs = []
    for k, v in content.items():
        if k.startswith('_'):
            continue
        try:
            pairs.append((int(k), v))
        except ValueError:
            raise SystemExit('content.json 键必须是整数段落号: %r' % (k,))
    for idx, segs in sorted(pairs):
        if idx >= len(ps):
            raise SystemExit('索引 %d 越界（段落总数 %d）' % (idx, len(ps)))
        set_para(ps[idx], segs)
    left = len(list(root.iter('{urn:schemas-microsoft-com:office:office}OLEObject')))
    print('replaced: %d, 残留 OLE: %d' % (len(pairs), left))
    if left:
        print('[!] 仍有 %d 个 OLE 公式未替换。若用整篇 doc-mode 转 MathType，'
              '这些既有公式会被反向转回 $...$；请先全部替换或改用 para 模式。' % left)
    items['word/document.xml'] = etree.tostring(
        root, xml_declaration=True, encoding='UTF-8', standalone=True)
    with zipfile.ZipFile(a.dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        for fn, data in items.items():
            zout.writestr(fn, data)
    print('Saved:', a.dst)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--dst', required=True)
    ap.add_argument('--content', required=True)
    main(ap.parse_args())