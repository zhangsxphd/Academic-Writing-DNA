#!/usr/bin/env python3
"""Offline inventory and *approximate* style metrics for an authorized manuscript corpus.

Supports .txt/.md directly, .pdf with optional pymupdf, .docx with optional python-docx.
Does not OCR, assess scientific accuracy, read image-based figure contents, or copy raw text.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

SUPPORTED = {'.txt', '.md', '.pdf', '.docx'}
IGNORE_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}
GENERIC_MARKERS = ('in recent years', 'it is worth noting', 'significantly improved',
                   '填补国内空白', '国际领先', '首次提出', '应用边界')


def read_document(path: Path) -> tuple[str, str, list[str], int | None]:
    warnings = []
    pages = None
    if path.suffix.lower() in {'.txt', '.md'}:
        content = path.read_bytes()
        try:
            return content.decode('utf-8-sig'), 'utf-8', warnings, pages
        except UnicodeDecodeError:
            try:
                return content.decode('utf-16'), 'utf-16', warnings, pages
            except UnicodeDecodeError:
                return '', 'decode_failed', ['文本编码无法可靠识别；请保存为 UTF-8'], pages
    if path.suffix.lower() == '.pdf':
        try:
            import fitz
        except ImportError:
            return '', 'pdf_unavailable', ['未安装 PyMuPDF（pip install pymupdf），无法提取 PDF'], pages
        try:
            with fitz.open(path) as doc:
                pages = len(doc)
                by_page = [page.get_text(sort=True) or '' for page in doc]
            text = '\n\n'.join(by_page)
            low_pages = sum(len(x.strip()) < 80 for x in by_page)
            if low_pages:
                warnings.append(f'{low_pages}/{pages} 页提取文字少于80字符，可能为扫描/图表页；须查看原始页面')
            warnings.append('PDF 提取文本无法替代图表、公式、双栏顺序和补充材料的页面核验')
            return text, 'pymupdf', warnings, pages
        except Exception as exc:
            return '', 'pdf_error', [f'PDF 提取失败：{type(exc).__name__}: {exc}'], pages
    if path.suffix.lower() == '.docx':
        try:
            from docx import Document
        except ImportError:
            return '', 'docx_unavailable', ['未安装 python-docx（pip install python-docx）'], pages
        try:
            doc = Document(str(path))
            paras = [x.text for x in doc.paragraphs if x.text.strip()]
            table_text = ['\t'.join(cell.text for cell in row.cells) for t in doc.tables for row in t.rows]
            if doc.tables:
                warnings.append('DOCX 含表格，已抽取单元格文字但未保留合并关系/表注位置')
            warnings.append('未检查图片、公式、文本框与修订批注')
            return '\n'.join(paras + table_text), 'python-docx', warnings, pages
        except Exception as exc:
            return '', 'docx_error', [f'DOCX 提取失败：{type(exc).__name__}: {exc}'], pages
    raise ValueError(f'Unsupported extension: {path.suffix}')


def metrics(text: str) -> dict:
    cleaned = re.sub(r'\s+', ' ', text).strip()
    english_words = re.findall(r"\b[A-Za-z]+(?:['’-][A-Za-z]+)*\b", text)
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    sentences = [x.strip() for x in re.split(r'[.!?。！？]+(?=\s|$|[\u4e00-\u9fff])', text) if x.strip()]
    paragraphs = [x.strip() for x in re.split(r'\n\s*\n', text) if x.strip()]
    return {
        'characters_nonspace': len(re.sub(r'\s+', '', text)),
        'english_word_count': len(english_words),
        'chinese_character_count': len(chinese_chars),
        'paragraph_count_approx': len(paragraphs),
        'sentence_count_approx': len(sentences),
        'sentence_length_chars_mean_approx': round(sum(len(x) for x in sentences) / len(sentences), 1) if sentences else None,
        'emdash_count': text.count('—') + text.count('–'),
        'candidate_cliches': {term: len(re.findall(re.escape(term), cleaned, re.I)) for term in GENERIC_MARKERS if re.search(re.escape(term), cleaned, re.I)},
    }


def audit(corpus: Path) -> dict:
    results = []
    hashes: dict[str, list[str]] = {}
    for path in sorted(corpus.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue
        if any(part in IGNORE_DIRS or part.startswith('.') for part in path.relative_to(corpus).parts):
            continue
        text, extractor, warnings, pages = read_document(path)
        rel = str(path.relative_to(corpus))
        norm_hash = hashlib.sha256(re.sub(r'\s+', '', text).lower().encode()).hexdigest() if text else None
        if norm_hash:
            hashes.setdefault(norm_hash, []).append(rel)
        item = {
            'file': rel, 'type': path.suffix.lower(), 'bytes': path.stat().st_size,
            'extraction': extractor, 'pdf_pages': pages,
            'text_extracted': bool(text.strip()), 'warnings': warnings,
            **metrics(text),
        }
        results.append(item)
    duplicates = [names for names in hashes.values() if len(names) > 1]
    full_text_candidates = sum(r['text_extracted'] for r in results)
    return {
        'corpus': str(corpus.resolve()), 'file_count': len(results),
        'extracted_count': full_text_candidates,
        'important_warning': '提取成功不等于已经阅读全文/图表/补充材料；质量及作者版权仍需人工核验。',
        'duplicate_text_groups': duplicates, 'files': results,
    }


def main():
    parser = argparse.ArgumentParser(description='科研语料离线清点与近似文本统计')
    parser.add_argument('--corpus', type=Path, required=True, help='存放有授权论文的目录')
    parser.add_argument('--out', type=Path, required=True, help='结果目录；不复制论文原文')
    args = parser.parse_args()
    if not args.corpus.is_dir():
        parser.error(f'语料目录不存在：{args.corpus}')
    if args.out.resolve() == args.corpus.resolve():
        parser.error('结果目录不能直接等于语料根目录')
    report = audit(args.corpus)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'corpus_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    if report['files']:
        with (args.out / 'corpus_inventory.csv').open('w', encoding='utf-8-sig', newline='') as f:
            keys = [key for key in report['files'][0] if key != 'candidate_cliches']
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            for record in report['files']:
                writer.writerow({**record, 'warnings': '；'.join(record['warnings'])})
    print(json.dumps({'files': report['file_count'], 'extracted': report['extracted_count'],
                      'duplicate_groups': len(report['duplicate_text_groups']),
                      'json': str(args.out / 'corpus_audit.json')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
