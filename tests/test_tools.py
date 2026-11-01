import sys
import tempfile
from pathlib import Path
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from corpus_audit import audit, metrics
from revision_guard import compare


class ToolTests(unittest.TestCase):
    def test_audit_duplicate_and_encoding(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / 'one.md').write_text('Introduction\n\nSoil carbon increased by 12%.', encoding='utf-8')
            (p / 'two.txt').write_text('Introduction\n\nSoil carbon increased by 12%.', encoding='utf-8')
            report = audit(p)
            self.assertEqual(report['file_count'], 2)
            self.assertEqual(len(report['duplicate_text_groups']), 1)
            self.assertEqual(report['extracted_count'], 2)

    def test_metrics(self):
        m = metrics('First sentence. Second sentence! 土壤碳。')
        self.assertGreaterEqual(m['english_word_count'], 4)
        self.assertEqual(m['chinese_character_count'], 3)

    def test_guard_reports_changed_data(self):
        result = compare('F-AM was 8.1 g/kg (p < 0.05).', 'F-AM was 9.2 g/kg (p < 0.01).')
        self.assertTrue(result['checks']['numbers_and_percentages']['needs_manual_review'])
        self.assertTrue(result['checks']['p_value_expressions']['needs_manual_review'])
        self.assertFalse(result['all_category_counts_unchanged'])

    def test_guard_unchanged(self):
        result = compare('T1 is 13%.', 'T1 is 13%.')
        self.assertTrue(result['all_category_counts_unchanged'])


if __name__ == '__main__':
    unittest.main()
