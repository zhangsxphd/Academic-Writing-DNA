#!/usr/bin/env python3
"""Conservative offline before/after token comparison. Flags potential changes; does NOT prove equivalence."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

NUMBER_RE = re.compile(r'(?<![A-Za-z\d])[-−]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:\s*[%‰])?(?![A-Za-z\d])')
DOI_RE = re.compile(r'\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+', re.I)
# Deliberately conservative: reliable exact form only. Not a general citation parser.
AUTHOR_YEAR_RE = re.compile(r'\b[A-Z][A-Za-z-]+\s+(?:et al\.?,?\s*)?\(?\d{4}[a-z]?\)?')
P_RE = re.compile(r'(?<![A-Za-z])p\s*[=<>≤≥]\s*0?\.\d+', re.I)
TREATMENT_RE = re.compile(r'\b(?:[A-Z]{1,5}-[A-Z0-9]{1,5}|T\d{1,3})\b')


def tokens(text: str) -> dict[str, Counter]:
    return {
        'numbers_and_percentages': Counter(re.sub(r'\s+', '', x) for x in NUMBER_RE.findall(text)),
        'doi': Counter(x.lower().rstrip('.,;)') for x in DOI_RE.findall(text)),
        'author_year_candidates': Counter(AUTHOR_YEAR_RE.findall(text)),
        'p_value_expressions': Counter(re.sub(r'\s+', '', x).lower() for x in P_RE.findall(text)),
        'treatment_code_candidates': Counter(TREATMENT_RE.findall(text)),
    }


def compare(before: str, after: str) -> dict:
    a = tokens(before)
    b = tokens(after)
    changes = {}
    for category in a:
        removed = list((a[category] - b[category]).elements())
        added = list((b[category] - a[category]).elements())
        changes[category] = {'removed_or_less_frequent': removed, 'added_or_more_frequent': added,
                             'needs_manual_review': bool(removed or added)}
    return {
        'warning': '候选差异检查（可能误报）。相同 token 数量也不代表表述、单位或因果关系保持不变。',
        'all_category_counts_unchanged': not any(x['needs_manual_review'] for x in changes.values()),
        'checks': changes,
    }


def main():
    parser = argparse.ArgumentParser(description='科研文稿修改前后事实锚点辅助核查')
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    before, _, bw, _ = read(args.before)
    after, _, aw, _ = read(args.after)
    if not before.strip() or not after.strip():
        parser.error('无法读取完整前后文：请检查扩展名、扫描 PDF 或空白文件')
    report = compare(before, after)
    report['source_files'] = {'before': str(args.before), 'after': str(args.after)}
    report['read_warnings'] = bw + aw
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'out': str(args.out), 'possible_changes': {k: v['needs_manual_review'] for k,v in report['checks'].items()}}, ensure_ascii=False))


def read(path: Path):
    from corpus_audit import read_document
    return read_document(path)


if __name__ == '__main__':
    main()
