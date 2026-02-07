import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import utils

class TestServices(unittest.TestCase):
    def test_check_ffmpeg(self):
        # This depends on the environment, but it should return True or False without error.
        result = utils.check_ffmpeg()
        print(f"FFmpeg detected: {result}")
        self.assertIsInstance(result, bool)

    def test_validate_pdf_no_file(self):
        valid, msg = utils.validate_pdf("non_existent_file.pdf")
        self.assertFalse(valid)
        self.assertIn("no existe", msg)

    def test_validate_pdf_bad_extension(self):
        with open("test.txt", "w") as f:
            f.write("test")
        valid, msg = utils.validate_pdf("test.txt")
        os.remove("test.txt")
        self.assertFalse(valid)
        self.assertIn("extensión", msg)

    def test_validate_pdf_bad_header(self):
        with open("fake.pdf", "wb") as f:
            f.write(b"NOT A PDF")
        valid, msg = utils.validate_pdf("fake.pdf")
        os.remove("fake.pdf")
        self.assertFalse(valid)
        self.assertIn("cabecera incorrecta", msg)

    def test_validate_pdf_valid(self):
        with open("good.pdf", "wb") as f:
            f.write(b"%PDF-1.4")
        valid, msg = utils.validate_pdf("good.pdf")
        os.remove("good.pdf")
        self.assertTrue(valid)
        self.assertIn("válido", msg)

if __name__ == '__main__':
    unittest.main()
