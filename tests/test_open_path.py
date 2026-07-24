import pytest
from unittest.mock import patch
from src.infrastructure.env_manager import open_path


class TestOpenPath:
    @patch("src.infrastructure.env_manager.platform.system", return_value="Windows")
    @patch("src.infrastructure.env_manager.os.startfile", create=True)
    def test_windows_uses_startfile(self, mock_startfile, mock_system):
        open_path("C:\\test\\file.mp3")
        mock_startfile.assert_called_once_with("C:\\test\\file.mp3")

    @patch("src.infrastructure.env_manager.platform.system", return_value="Linux")
    @patch("src.infrastructure.env_manager.subprocess.run")
    def test_linux_uses_xdg_open(self, mock_run, mock_system):
        open_path("/tmp/test.mp3")
        mock_run.assert_called_once_with(["xdg-open", "/tmp/test.mp3"], check=False)

    @patch("src.infrastructure.env_manager.platform.system", return_value="Darwin")
    @patch("src.infrastructure.env_manager.subprocess.run")
    def test_darwin_uses_open(self, mock_run, mock_system):
        open_path("/tmp/test.mp3")
        mock_run.assert_called_once_with(["open", "/tmp/test.mp3"], check=False)

    @patch("src.infrastructure.env_manager.platform.system", return_value="Linux")
    @patch("src.infrastructure.env_manager.subprocess.run", side_effect=FileNotFoundError)
    def test_raises_on_missing_binary(self, mock_run, mock_system):
        with pytest.raises(RuntimeError, match="xdg-utils"):
            open_path("/tmp/test.mp3")
