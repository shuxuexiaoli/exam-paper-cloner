#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""试卷版式微调：修复第 1 页装订线过高、并给第 2 页题目加段前距填满页面。

背景：试卷正文在 <w:tbl> 内，每页是一个定高表格行。
  * row0 含左侧竖排"装订线"块(P1..P35)，若按 1.5 倍行距会高达 ~805pt，
    超过页面正文高 754pt，Word/WPS 会把整块正文推到第 2 页，形成"第 1 页只有标题"。
  * 第 2 页 = row9 (h=14996 twips, hRule=exact)，内容止于 y≈648 时底部余 ~150pt，
    需在各题段前均摊补足（见 GAPS）。

用法：
  python fix_layout.py <docx> [--before 120] [--sidebar] [-o out.docx] [--measure-only]

  --before N   给第 2 页 17 处题段前加 N twips（1pt = 20 twips）
  --sidebar    把 P1..P35 装订线行距改为 line=240 exact
  --measure-only  只打印当前各段间距值，不改文件

参考值：正文底边 y=799.4pt(基于 pgMar top/bottom=851 twips)，第 2 页目标
底部留白 ~40pt → 需要总量 ≈ (792.4 - 40 - 实测末行y)。17 处均摊后 ×20 得 twips。
"""
import argparse
import shutil
import sys
import zipfile

from lxml import etree

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
SIDEBAR = list(range(1, 36))
GAPS = [117, 118, 119, 120, 121, 122, 123, 124, 125,
        126, 127, 128, 129, 134, 135, 137, 139]


def load(path):
    with zipfile.ZipFile(path) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    data = {i.filename: d for i, d in items}
    return items, data, etree.fromstring(data["word/document.xml"])


def save(path, items, data, root):
    data["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for info, _ in items:
            z.writestr(info, data[info.filename])


def spacing(p, create):
    pPr = p.find(W + "pPr")
    if pPr is None:
        if not create:
            return None
        pPr = etree.Element(W + "pPr")
        p.insert(0, pPr)
    sp = pPr.find(W + "spacing")
    if sp is None and create:
        sp = etree.Element(W + "spacing")
        pPr.append(sp)
    return sp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--before", type=int, default=0)
    ap.add_argument("--sidebar", action="store_true")
    ap.add_argument("-o", "--out")
    ap.add_argument("--measure-only", action="store_true")
    a = ap.parse_args()

    items, data, root = load(a.docx)
    ps = list(root.iter(W + "p"))
    print("paragraphs=%d" % len(ps))

    if a.measure_only:
        for i in GAPS:
            sp = spacing(ps[i], False)
            txt = "".join(t.text or "" for t in ps[i].iter(W + "t"))[:16]
            print("P%-4d before=%-5s line=%-5s rule=%-8s %s" % (
                i, sp.get(W + "before") if sp is not None else "-",
                sp.get(W + "line") if sp is not None else "-",
                sp.get(W + "lineRule") if sp is not None else "-", txt))
        return

    if a.sidebar:
        for i in SIDEBAR:
            sp = spacing(ps[i], True)
            sp.set(W + "line", "240")
            sp.set(W + "lineRule", "exact")
        print("sidebar: P1..P35 -> line=240 exact")

    if a.before > 0:
        for i in GAPS:
            spacing(ps[i], True).set(W + "before", str(a.before))
        print("page2: %d gaps -> before=%d twips (%.1fpt each)"
              % (len(GAPS), a.before, a.before / 20.0))

    out = a.out or a.docx
    save(out, items, data, root)
    print("saved:", out)


if __name__ == "__main__":
    sys.exit(main())
