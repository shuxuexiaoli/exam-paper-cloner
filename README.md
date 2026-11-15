# exam-paper-cloner — 试卷克隆技能（docx → 平行卷）

拿一份现成的试卷 `.docx` 当模板，**只替换题目和答案的文字，版式、表格、装订线、自动编号全部不动**，生成同版式、同题型的平行新卷（A 卷 / B 卷），公式最终交付为 MathType 对象。

## 适用场景

- 「按这套卷的格式再出一套」「出平行卷 / B 卷」「分析这份试卷的结构」
- 不适用：从零排版新试卷；只需要把 LaTeX 转公式（用 [mathtype-word-latex](https://github.com/shuxuexiaoli/mathtype-word-latex)）

## 工作方式

技能内置五道硬门槛，逐步验收、不过不许进下一步：盘点模板结构 → 生成新卷并确保公式段全覆盖（残留 OLE 为 0）→ 公式预检 → 版式修复 → 交付前验证。判据全部量化，不靠肉眼翻页。

## 仓库结构

```
exam-paper-cloner/
├── SKILL.md                  # 技能说明：完整流程与五道门槛的判定规则
└── scripts/
    ├── inventory.py          # 盘点模板试卷的结构与段落索引
    ├── gen_exam_parallel.py  # 按模板生成平行新卷
    ├── precheck_formulas.py  # 公式预检
    ├── fix_layout.py         # 版式修复
    ├── set_position_std.py   # 定位标准化
    ├── verify.py             # 交付前验证
    └── content_template.json # 题目内容模板
```

## 使用方式

本仓库是一份给 AI 助手加载的技能（skill）：把 `SKILL.md` 与 `scripts/` 提供给助手，并给一份模板试卷 `.docx`，即可按流程产出平行卷。公式转 MathType 的环节与 mathtype-word-latex 技能配合完成。

> 作者为职业院校数学教师，更多教学工具见主页：https://github.com/shuxuexiaoli
