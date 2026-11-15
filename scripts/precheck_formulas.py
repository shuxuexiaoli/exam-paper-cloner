# -*- coding: utf-8 -*-
"""转换 MathType 前预检：列出不可被 MathType 接受的 $...$ 公式。

放行规则（与 mathtype-word-latex 的 Toggle 判据一致）：
  · 单字符（字母/数字/CJK 以外符号）
  · 纯数字或小数，如 3 / 30 / 0.5
  · 含 ^ _ + - * / = ( ) < > { } 或反斜杠
其余（如 a,b）会被 MathType 判为"不像公式"，必须改写。

用法: python precheck_formulas.py 新卷.docx
退出码: 0=全部可转换  1=存在不可转换公式
"""
import re
import sys
import zipfile

NUMERIC = re.compile(r'^-?\d+(\.\d+)?$')
OPERATORS = re.compile(r'[\^_+\-*/=()<>{}\\]')


def convertible(s):
    s = s.strip()
    if not s:
        return False
    if len(s) == 1:
        return True
    if NUMERIC.match(s):
        return True
    return bool(OPERATORS.search(s))


def main(path):
    x = zipfile.ZipFile(path).read('word/document.xml').decode('utf-8')
    spans = re.findall(r'\$([^$\n]{1,2000})\$', x)
    bad = [s for s in spans if not convertible(s)]
    print('spans:', len(spans))
    if bad:
        print('不可转换(裸多字母/无运算符/空):')
        for s in bad:
            print('   $%s$' % s)
        raise SystemExit(1)
    print('全部可转换')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'new_exam.docx')
