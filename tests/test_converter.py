import unittest
from unittest.mock import patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import mp3_converter

class TestMp3Converter(unittest.TestCase):
    
    @patch('services.mp3_converter.subprocess.run')
    @patch('os.path.exists')
    def test_convert_success(self, mock_exists, mock_run):
        # Mock exists to pass initial check and final check
        mock_exists.return_value = True
        
        wav_path = "output/test/final/audio.wav"
        
        # Act
        mp3_path = mp3_converter.convert_wav_to_mp3(wav_path)
        
        # Assert
        self.assertTrue(mp3_path.endswith(".mp3"))
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn("ffmpeg", args)
        self.assertIn("libmp3lame", args)

    @patch('os.path.exists')
    def test_convert_input_not_found(self, mock_exists):
        mock_exists.return_value = False
        
        with self.assertRaises(Exception) as cm:
            mp3_converter.convert_wav_to_mp3("fake.wav")
            
        self.assertIn("not found", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
