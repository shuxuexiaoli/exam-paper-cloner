# -*- coding: utf-8 -*-
"""盘点 docx 试卷：输出每个段落的 索引/是否在表格/公式(OLE)数/文本。
用法: python inventory.py 模板.docx
输出格式: P<索引> tbl=True/False obj=<OLE数> :: <文本>
"""
import sys
import zipfile
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
O = '{urn:schemas-microsoft-com:office:office}'
NS = {'w': W[1:-1]}


def ins_tbl(p):
    a = p.getparent()
    while a is not None:
        if a.tag == W + 'tbl':
            return True
        a = a.getparent()
    return False


def main(path):
    xml = zipfile.ZipFile(path).read('word/document.xml')
    root = etree.fromstring(xml)
    lines = []
    n = 0
    for p in root.iter(W + 'p'):
        text = ''.join(t.text or '' for t in p.iter(W + 't'))
        objs = len(p.findall('.//' + O + 'OLEObject'))
        if text.strip() or objs:
            lines.append('P%d tbl=%s obj=%d :: %s' % (n, ins_tbl(p), objs, text))
        n += 1
    lines.append('total paras: %d' % n)
    print('\n'.join(lines))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'template.docx')