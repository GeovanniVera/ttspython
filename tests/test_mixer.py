import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import audio_mixer

class TestAudioMixer(unittest.TestCase):
    
    @patch('services.audio_mixer.subprocess.run')
    @patch('services.audio_mixer.get_ffmpeg_exe')
    @patch('os.path.exists')
    def test_mix_audio_command_structure(self, mock_exists, mock_get_ffmpeg, mock_run):
        # Setup
        mock_exists.return_value = True
        mock_get_ffmpeg.return_value = "ffmpeg_mock"
        
        voice_path = "voice.wav"
        bgm_path = "bgm.mp3"
        output_path = "mixed.wav"
        
        # Act
        audio_mixer.mix_audio(voice_path, bgm_path, output_path, voice_vol=1.5, bgm_vol=0.5)
        
        # Assert
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0] # The command list
        
        # Check executable
        self.assertEqual(args[0], "ffmpeg_mock")
        
        # Check inputs and loop
        # Expected: -i voice -stream_loop -1 -i bgm
        try:
            voice_idx = args.index(voice_path)
            bgm_idx = args.index(bgm_path)
            loop_idx = args.index("-stream_loop")
        except ValueError:
            self.fail("Missing input paths or stream_loop flag")
            
        self.assertTrue(args[voice_idx - 1] == "-i")
        self.assertTrue(args[bgm_idx - 1] == "-i")
        
        # Check loop is before bgm and after voice (in terms of arg order it appears before the second input)
        # Actually in the code: [exe, -i, voice, -stream_loop, -1, -i, bgm]
        self.assertEqual(args[2], voice_path)
        self.assertEqual(args[3], "-stream_loop")
        self.assertEqual(args[4], "-1")
        self.assertEqual(args[6], bgm_path)
        
        # Check filter complex
        filter_arg = args[args.index("-filter_complex") + 1]
        self.assertIn("volume=1.5", filter_arg)
        self.assertIn("volume=0.5", filter_arg)
        self.assertIn("amix=inputs=2:duration=first", filter_arg)
        
        # Check creation flags (Windows specific)
        kwargs = mock_run.call_args[1]
        self.assertEqual(kwargs.get('creationflags'), 0x08000000)

if __name__ == "__main__":
    print("Running tests...")
    unittest.main()
