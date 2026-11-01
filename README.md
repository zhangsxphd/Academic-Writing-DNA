# Academic-Writing-DNA

**Evidence-first academic writing workflows for SCI manuscripts and National Natural Science Foundation of China (NSFC) proposals.**

**以科学证据和研究逻辑为先的科研写作 Skill，面向英文 SCI 论文与中文国家自然科学基金申请书。**

> Status: **v0.1.0, early working version**. Local unit tests pass, but effectiveness has not yet been validated against a representative corpus of real SCI manuscripts and grant proposals.
>
> 版本说明：目前已完成工作流及基础脚本测试，尚未完成真实论文和基金申请书语料的效果验证。

## Why this project?

Academic-Writing-DNA provides a scientific writing workflow that separates evidence evaluation, study-design review, manuscript structure, and language revision. It prioritizes research questions, statistical evidence, citation integrity, and defensible claims **before** wording and style.

它的目标是让 AI 在起草、修改论文时始终区分“写得像高水平论文”和“研究有真实科学依据”。所有写作规范均可修订，所有重要主张均应可追溯到原始证据。

## Features | 功能

| Workflow / 模式 | Purpose / 用途 |
| --- | --- |
| `DISTILL` | Extract traceable writing patterns from a licensed corpus; distinguish style from scientific content. 从授权语料提炼可追溯写作规则。 |
| `SCI_WRITE` / `SCI_EDIT` | Draft or revise the Introduction, Methods, Results, Discussion, and Abstract of English scientific manuscripts. |
| `NSFC_WRITE` / `NSFC_EDIT` | Organize a grant proposal around a precise research question, testable hypotheses, study design, and feasibility. |
| `STYLE_AUDIT` | Reduce vague or repetitive wording without changing scientific facts or inference strength. |
| `INTEGRITY_AUDIT` | Check design, replication, numerical anchors, terminology, citations, and consistency between sections. |

**Supported disciplinary context:** agricultural water management, irrigation, soil science, plant-water relations, soil carbon and nitrogen cycling, microbial ecology, environmental monitoring, and related agricultural engineering research. The rules are editable and can be adapted to other fields.

## Quick start | 快速开始

### Install for Codex

Clone into a user skills directory (choose one location supported by your Codex installation):

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/zhangsxphd/Academic-Writing-DNA.git \
  ~/.codex/skills/academic-writing-dna
```

Reload Codex and explicitly invoke `$academic-writing-dna`. If your Codex environment uses `~/.agents/skills`, install there instead; do not maintain divergent copies.

### Example: review an SCI Introduction

```text
Use $academic-writing-dna in SCI_EDIT mode.
Read my Introduction and the supporting sources actually available in this project.
First identify weaknesses in the research question, literature synthesis and hypotheses.
Then provide a minimally revised, publication-ready version.
Preserve results, citations, treatment labels, uncertainty and inference strength.
Report what could not be verified.
```

### 示例：修改国家自然科学基金申请书

```text
使用 $academic-writing-dna 的 NSFC_EDIT 模式。
先检查立项依据中的科学问题、研究假设、研究内容和实验方案是否前后对应。
区分已有文献已经证明的事实、合理推论和未经验证的假设。
仅在实际可读取的证据范围内修改，避免口号化表达和夸大创新性。
输出主要问题、依据、修改建议和完整修改稿。
```

### 示例：提炼 SCI Introduction 的 Writing DNA

```text
使用 $academic-writing-dna 的 DISTILL 模式。
分析 ./corpus/sci-introduction 中我有权使用的论文。
先清点语料、去重并记录全文/部分可读取的情况。
只分析 Introduction 的论证结构、引用习惯与语言表达。
重要规则逐条附语料 ID、原文位置、例外和可信程度。
将结果写入本项目的 Writing-DNA.md，不复制范文的科学结论。
```

## Offline scripts | 离线辅助脚本

No external network service or API key is required. Python 3 is sufficient for the built-in tests and plain text inputs.

```bash
python3 -m unittest discover -s tests -v

# Inventory and approximate textual statistics (TXT/MD/PDF/DOCX)
python3 scripts/corpus_audit.py --corpus /path/to/authorized/corpus --out /path/to/audit

# Compare scientific tokens between two manuscript versions
python3 scripts/revision_guard.py --before /path/to/before.txt --after /path/to/after.txt --out /path/to/diff.json
```

For optional PDF/DOCX extraction:

```bash
python3 -m pip install -r requirements-optional.txt
```

`corpus_audit.py` extracts text and flags possible duplicates, incomplete extraction and approximate language metrics. **It does not read figures, verify references, inspect formulas accurately, or evaluate paper quality.**

`revision_guard.py` flags differences in numbers, DOI strings, author-year candidates, P-value expressions and treatment identifiers. **Equal token counts do not prove that a scientific claim is unchanged.** Always review the actual manuscript and the source evidence.

## Repository layout | 项目结构

```text
Academic-Writing-DNA/
├── SKILL.md                        # Entry point for Codex
├── agents/openai.yaml              # Skill metadata
├── references/
│   ├── sci.md                      # SCI writing and editing
│   ├── nsfc.md                     # NSFC proposal writing
│   ├── distill.md                  # Corpus-based writing DNA
│   ├── revision-gates.md           # Scientific integrity review
│   └── user-profile.md             # Editable default writing preferences
├── scripts/
│   ├── corpus_audit.py
│   └── revision_guard.py
├── templates/
│   ├── Writing-DNA.template.md
│   └── project-context.template.md
├── tests/test_tools.py
├── README.md
└── LICENSE
```

## Scientific integrity and privacy | 科学规范与隐私

- Use **only** materials you are authorized to process. Keep copyrighted journal PDFs, confidential proposals, unpublished datasets and identifiable information outside public repositories.
- A writing DNA describes **rhetorical and organizational patterns**. It is not evidence for novelty, hypotheses, methods, results, or causality.
- Distinguish full-text access from an abstract or partial extraction. Never invent citations, numerical values, page numbers, findings or reviewer responses.
- Respect the target journal's or funder's current instructions; they override general style preferences.
- Avoid assigning an invented “AI content score,” acceptance probability or originality percentage.
- The editable `references/user-profile.md` is included as a sample of discipline-specific preferences; review it before making the repository public or adapting this skill to other users.

## Scope and roadmap | 范围与后续计划

v0.1.0 includes a reproducible set of instructions, templates, two lightweight local scripts, and unit tests. Future improvements may include annotated discipline-specific corpus examples **where distribution rights permit**, more robust reference checking, and blinded before/after manuscript evaluation. Those improvements are not implemented yet.

## License | 开源许可

Copyright (c) 2026 zhangsxphd. Released under the [MIT License](LICENSE).

本项目代码、文档和模板采用 MIT License 开源。科研论文、基金申请书、原始数据和第三方文献不属于本项目的开源内容，请按照相关版权和保密要求独立管理。

---

**Project description for GitHub / 仓库简介**

> Evidence-first Codex Skill for SCI manuscript writing, NSFC grant proposals, academic style distillation, and scientific integrity checks. | 面向 SCI 论文与国家自然科学基金申请书的科研写作 Skill。

**Suggested topics:** `codex-skill`, `academic-writing`, `scientific-writing`, `research`, `nsfc`, `sci-paper`, `writing-dna`, `python`
