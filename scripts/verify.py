# -*- coding: utf-8 -*-
"""转换后校验（第 5 步硬门槛）。

判定：
  · 残留 $...$ 必须为 0        —— 否则有公式没被 MathType 吃掉（硬失败）
  · Equation.DSMT4 必须 > 0    —— 否则转换整体没生效（硬失败）
  · OLE 与 DSMT4 数不相等      —— 警告：说明存在非 Equation.DSMT4 的 OLE
                                  （旧 Equation.3 / 嵌入对象），加 --strict 升级为失败
  · 四大题标题 + 答案页标题     —— 缺任一则版式被破坏（硬失败）

用法: python verify.py 新卷.docx [--strict]
退出码: 0=通过  1=失败
"""
import re
import sys
import zipfile
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
TITLES = ('第一题', '第二题', '第三题', '第四题', '答案及评分标准')


def main(path, strict=False):
    x = zipfile.ZipFile(path).read('word/document.xml').decode('utf-8')
    ole = x.count('<o:OLEObject')
    dsmt = x.count('Equation.DSMT4')
    resid = len(re.findall(r'\$[^$\n]{1,2000}\$', x))
    root = etree.fromstring(x.encode('utf-8'))
    txt = ''.join(t.text or '' for t in root.iter(W + 't'))

    print('OLEObject     :', ole)
    print('Equation.DSMT4:', dsmt)
    print('residual $..$ :', resid)
    fails = []
    for key in TITLES:
        ok = key in txt
        print('contains %-12s: %s' % (key, ok))
        if not ok:
            fails.append('缺少标题「%s」' % key)
    if resid:
        fails.append('残留 %d 个 $...$ 未转 MathType' % resid)
    if dsmt == 0:
        fails.append('没有任何 Equation.DSMT4，转换未生效')
    if ole != dsmt:
        msg = 'OLE(%d) ≠ DSMT4(%d)，差 %d 个' % (ole, dsmt, abs(ole - dsmt))
        if strict:
            fails.append(msg + '（--strict 判失败）')
        else:
            print('[!] 警告:', msg, '—— 若确有非 MathType 的 OLE 对象可忽略，'
                  '否则说明有公式没转成功；加 --strict 可强制失败。')
    if fails:
        print('\n[FAIL] ' + '；'.join(fails))
        raise SystemExit(1)
    print('\n[PASS] 公式与版式校验通过')


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    main(args[0] if args else 'new_exam.docx', strict='--strict' in sys.argv)
