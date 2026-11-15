# -*- coding: utf-8 -*-
"""把 docx 全部 run 的字符位置(w:position)统一为 0（字体"位置=标准"）。
用法: python set_position_std.py 输入.docx 输出.docx
"""
import re
import sys
import zipfile

PAT = re.compile(r'<w:position w:val="-?\d+"\s*/>')


def main(src, dst):
    with zipfile.ZipFile(src) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    n = 0
    out = []
    for i, data in items:
        if i.filename == 'word/document.xml':
            xml = data.decode('utf-8')
            xml, n = PAT.subn('<w:position w:val="0"/>', xml)
            data = xml.encode('utf-8')
        out.append((i, data))
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
        for i, data in out:
            z.writestr(i, data)
    print('positions normalized:', n)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise SystemExit('用法: python set_position_std.py 输入.docx 输出.docx')
    main(sys.argv[1], sys.argv[2])