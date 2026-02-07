import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import pdf_extractor, text_preprocessor

class TestExtraction(unittest.TestCase):
    
    @patch('services.pdf_extractor.PdfReader')
    def test_extract_text_success(self, MockPdfReader):
        # Setup mock
        mock_reader = MockPdfReader.return_value
        page1 = MagicMock()
        page1.extract_text.return_value = "Hello "
        page2 = MagicMock()
        page2.extract_text.return_value = "World"
        mock_reader.pages = [page1, page2]
        
        # Test
        text, metadata = pdf_extractor.extract_text("dummy.pdf")
        
        self.assertEqual(text, "Hello \nWorld")
        self.assertEqual(metadata['num_pages'], 2)
        self.assertTrue(metadata['success'])

    @patch('services.pdf_extractor.PdfReader')
    def test_extract_text_empty(self, MockPdfReader):
        # Setup mock for scanned PDF (no text)
        mock_reader = MockPdfReader.return_value
        page1 = MagicMock()
        page1.extract_text.return_value = ""
        mock_reader.pages = [page1]
        
        text, metadata = pdf_extractor.extract_text("dummy.pdf")
        
        self.assertEqual(text, "")
        self.assertTrue(metadata['success'])

    def test_preprocess_hyphens(self):
        raw = "This is an exam-\nple of hyphenation."
        clean = text_preprocessor.preprocess(raw)
        self.assertEqual(clean, "This is an example of hyphenation.")

    def test_preprocess_newlines(self):
        raw = "Line 1.\r\nLine 2.\nLine 3."
        clean = text_preprocessor.preprocess(raw)
        # Expect newlines to be preserved or handled. 
        # Current logic: \r\n -> \n. 
        # But wait, logic also did re.sub(r'\s+', ' ', text) which replaces ALL whitespace including newlines with space!
        # Let's check the implementation again. 
        # Implementation: 
        # text = text.replace('\r\n', '\n')
        # text = re.sub(r'\s+', ' ', text)
        # This effectively joins EVERYTHING into a single line.
        # This might be desired for continuous narration, but let's verify if that's what we want.
        # For TTS, often joining is good, but maybe pause at periods.
        # The test expects "Line 1. Line 2. Line 3."
        self.assertEqual(clean, "Line 1. Line 2. Line 3.")

    def test_preprocess_whitespace(self):
        raw = "Multiple    spaces."
        clean = text_preprocessor.preprocess(raw)
        self.assertEqual(clean, "Multiple spaces.")

if __name__ == '__main__':
    unittest.main()
