import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import wav_merger

class TestWavMerger(unittest.TestCase):
    
    @patch('services.wav_merger.subprocess.run')
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_merge_wavs_success(self, mock_open, mock_exists, mock_run):
        # Mock file existence checks
        # 1. Base dir check -> True
        # 2. Chunk files check -> True for loop
        mock_exists.return_value = True
        
        base_dir = "output/Test/chunks"
        base_name = "Test"
        total = 3
        
        # Act
        final_path = wav_merger.merge_wavs(base_dir, base_name, total)
        
        # Assert FFmpeg called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "ffmpeg")
        self.assertIn("concat", args)
        
        # Verify result path
        self.assertTrue("final" in final_path)
        self.assertTrue("Test_final.wav" in final_path)

    @patch('os.path.exists')
    def test_merge_wavs_missing_too_many(self, mock_exists):
        # Mock base dir exists, but chunks don't
        def side_effect(path):
            if "chunks" in path and "wav" not in path:
                return True # Dir exists
            return False # Files don't
            
        mock_exists.side_effect = side_effect
        
        with self.assertRaises(Exception) as cm:
            wav_merger.merge_wavs("chunks", "base", 10)
        
        self.assertIn("Too many missing chunks", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
