import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import shutil

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import chunker, output_manager, tts_engine

class TestTTSFlow(unittest.TestCase):
    
    def test_chunker_small(self):
        text = "One two three four five."
        chunks = chunker.chunk_text(text, word_limit=2)
        # Expected: ["One two", "three four", "five."]
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], "One two")

    def test_output_manager_structure(self):
        pdf_name = "Test_Document.pdf"
        chunks_dir = output_manager.prepare_output_structure(pdf_name)
        
        self.assertTrue(os.path.exists(chunks_dir))
        self.assertTrue("Test_Document" in chunks_dir)
        self.assertTrue("output" in chunks_dir)
        
        # Cleanup
        try:
            shutil.rmtree("output")
        except:
            pass

    def test_filename_generation(self):
        name = output_manager.get_chunk_filename("dir", "Base", 1, 10)
        # Should be dir/Base_01.wav (since 10 has 2 digits)
        self.assertTrue("Base_01.wav" in name or "Base\\01.wav" in name)

    @patch('services.tts_engine.pyttsx3')
    def test_tts_save(self, mock_pyttsx3):
        # Mock engine
        mock_engine_instance = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine_instance
        
        engine = tts_engine.TTSEngine()
        
        # Mock os.path.exists to pass validation
        with patch('os.path.exists', return_value=True):
            engine.save_to_file("text", "test.wav")
            
        # Verify calls
        mock_engine_instance.save_to_file.assert_called_with("text", "test.wav")
        mock_engine_instance.runAndWait.assert_called_once()

if __name__ == "__main__":
    unittest.main()
