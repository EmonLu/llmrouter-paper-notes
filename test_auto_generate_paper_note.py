import importlib.util
import unittest
from pathlib import Path

SCRIPT_PATH = Path('/home/jiehui/llmrouter/llmrouter-paper-notes/auto_generate_paper_note.py')
spec = importlib.util.spec_from_file_location('auto_generate_paper_note', SCRIPT_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AutoGeneratePaperNoteTests(unittest.TestCase):
    def test_extract_arxiv_id_from_abs_url(self):
        self.assertEqual(mod.extract_arxiv_id('https://arxiv.org/abs/2601.17814'), '2601.17814')

    def test_extract_arxiv_id_from_pdf_url(self):
        self.assertEqual(mod.extract_arxiv_id('https://arxiv.org/pdf/2601.17814.pdf'), '2601.17814')

    def test_extract_arxiv_id_from_versioned_abs_url(self):
        self.assertEqual(mod.extract_arxiv_id('https://arxiv.org/abs/2605.18859v1'), '2605.18859')

    def test_is_url_detects_http_inputs(self):
        self.assertTrue(mod.is_url('https://arxiv.org/abs/2601.17814'))
        self.assertTrue(mod.is_url('http://example.com/paper.pdf'))
        self.assertFalse(mod.is_url('/tmp/paper.pdf'))

    def test_arxiv_abs_to_pdf_url(self):
        self.assertEqual(
            mod.normalize_arxiv_url('https://arxiv.org/abs/2601.17814'),
            'https://arxiv.org/pdf/2601.17814.pdf',
        )

    def test_arxiv_pdf_url_stays_pdf_url_without_version(self):
        self.assertEqual(
            mod.normalize_arxiv_url('https://arxiv.org/pdf/2601.17814.pdf'),
            'https://arxiv.org/pdf/2601.17814.pdf',
        )

    def test_arxiv_pdf_url_drops_version_suffix(self):
        self.assertEqual(
            mod.normalize_arxiv_url('https://arxiv.org/pdf/2605.18859v2.pdf'),
            'https://arxiv.org/pdf/2605.18859.pdf',
        )


if __name__ == '__main__':
    unittest.main()
