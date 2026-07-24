import os
import pytest
import threading
from unittest.mock import MagicMock
from src.infrastructure.repositories.cache_repository import CacheRepository
from src.domain.models.voice_settings import VoiceSettings


class TestCacheRepository:
    def test_key_includes_all_params(self):
        """Cache key changes when any parameter changes."""
        repo = CacheRepository(cache_dir="/tmp/test_cache")
        key1 = repo._generate_key("hello", "es-MX-JorgeNeural", "+0%", "+0Hz")
        key2 = repo._generate_key("hello", "es-MX-JorgeNeural", "+10%", "+0Hz")
        key3 = repo._generate_key("hello", "es-MX-JorgeNeural", "+0%", "+5Hz")
        key4 = repo._generate_key("world", "es-MX-JorgeNeural", "+0%", "+0Hz")
        assert key1 != key2
        assert key1 != key3
        assert key1 != key4

    def test_save_and_get(self, tmp_path):
        """Saved audio is retrievable."""
        repo = CacheRepository(cache_dir=str(tmp_path))
        src = tmp_path / "source.mp3"
        src.write_bytes(b"fake mp3 data")

        repo.save_audio("hello world", "voice1", "+0%", "+0Hz", str(src))
        result = repo.get_audio("hello world", "voice1", "+0%", "+0Hz")
        assert result is not None
        assert os.path.exists(result)

    def test_get_miss(self, tmp_path):
        """Non-cached text returns None."""
        repo = CacheRepository(cache_dir=str(tmp_path))
        result = repo.get_audio("not cached", "voice1", "+0%", "+0Hz")
        assert result is None

    def test_clear(self, tmp_path):
        """Clear removes all cached files."""
        repo = CacheRepository(cache_dir=str(tmp_path))
        src = tmp_path / "source.mp3"
        src.write_bytes(b"fake mp3 data")
        repo.save_audio("text", "v", "+0%", "+0Hz", str(src))
        assert repo.get_audio("text", "v", "+0%", "+0Hz") is not None

        repo.clear()
        assert repo.get_audio("text", "v", "+0%", "+0Hz") is None

    def test_concurrent_writes_no_corruption(self, tmp_path):
        """Multiple threads writing the same chunk don't corrupt the file."""
        repo = CacheRepository(cache_dir=str(tmp_path))
        src = tmp_path / "source.mp3"
        src.write_bytes(b"fake audio data")

        errors = []

        def save_chunk():
            try:
                repo.save_audio("identical text", "voice", "+0%", "+0Hz", str(src))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=save_chunk) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        result = repo.get_audio("identical text", "voice", "+0%", "+0Hz")
        assert result is not None


class TestCacheWiring:
    def test_first_run_misses_cache_generates_audio(self, tmp_path):
        """First execution: no cache -> calls TTS -> saves to cache."""
        from src.application.use_cases.process_pdf_to_speech import ProcessPdfToSpeechUseCase

        cache = CacheRepository(cache_dir=str(tmp_path / "cache"))
        generator = MagicMock()
        processor = MagicMock()
        text_service = MagicMock()
        text_service.chunk_text.return_value = ["chunk one"]

        # Generator mock must create the file so save_audio can copy it
        def fake_generate(text, path, settings):
            with open(path, "wb") as f:
                f.write(b"fake audio")
        generator.generate_speech.side_effect = fake_generate

        uc = ProcessPdfToSpeechUseCase(
            extractor=MagicMock(),
            generator=generator,
            processor=processor,
            text_service=text_service,
            cache_repo=cache,
        )

        settings = VoiceSettings(voice_id="test-voice", rate="+0%", pitch="+0Hz")
        processor.merge_wavs.return_value = "merged.mp3"
        processor.mix_with_bgm.return_value = "final.mp3"

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = uc.execute(
            text="chunk one",
            pdf_path=str(tmp_path / "test.pdf"),
            output_base_dir=str(output_dir),
            voice_settings=settings,
        )

        generator.generate_speech.assert_called_once()
        cached = cache.get_audio("chunk one", "test-voice", "+0%", "+0Hz")
        assert cached is not None

    def test_second_run_hits_cache_skips_tts(self, tmp_path):
        """Second execution: cache exists -> skips TTS."""
        from src.application.use_cases.process_pdf_to_speech import ProcessPdfToSpeechUseCase

        cache = CacheRepository(cache_dir=str(tmp_path / "cache"))
        generator = MagicMock()
        processor = MagicMock()
        text_service = MagicMock()
        text_service.chunk_text.return_value = ["chunk one"]

        # Pre-populate cache
        src = tmp_path / "prebuilt.mp3"
        src.write_bytes(b"cached audio")
        cache.save_audio("chunk one", "test-voice", "+0%", "+0Hz", str(src))

        uc = ProcessPdfToSpeechUseCase(
            extractor=MagicMock(),
            generator=generator,
            processor=processor,
            text_service=text_service,
            cache_repo=cache,
        )

        settings = VoiceSettings(voice_id="test-voice", rate="+0%", pitch="+0Hz")
        processor.merge_wavs.return_value = "merged.mp3"
        processor.mix_with_bgm.return_value = "final.mp3"

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = uc.execute(
            text="chunk one",
            pdf_path=str(tmp_path / "test.pdf"),
            output_base_dir=str(output_dir),
            voice_settings=settings,
        )

        generator.generate_speech.assert_not_called()

    def test_different_voice_settings_miss_cache(self, tmp_path):
        """Different voice -> cache miss."""
        from src.application.use_cases.process_pdf_to_speech import ProcessPdfToSpeechUseCase

        cache = CacheRepository(cache_dir=str(tmp_path / "cache"))
        generator = MagicMock()
        processor = MagicMock()
        text_service = MagicMock()
        text_service.chunk_text.return_value = ["chunk one"]

        # Pre-populate cache with voice A
        src = tmp_path / "prebuilt.mp3"
        src.write_bytes(b"cached audio")
        cache.save_audio("chunk one", "voice-A", "+0%", "+0Hz", str(src))

        uc = ProcessPdfToSpeechUseCase(
            extractor=MagicMock(),
            generator=generator,
            processor=processor,
            text_service=text_service,
            cache_repo=cache,
        )

        # Request with voice B
        settings = VoiceSettings(voice_id="voice-B", rate="+0%", pitch="+0Hz")
        processor.merge_wavs.return_value = "merged.mp3"
        processor.mix_with_bgm.return_value = "final.mp3"

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = uc.execute(
            text="chunk one",
            pdf_path=str(tmp_path / "test.pdf"),
            output_base_dir=str(output_dir),
            voice_settings=settings,
        )

        generator.generate_speech.assert_called_once()

    def test_no_cache_repo_still_works(self, tmp_path):
        """Use case works without cache_repo (backward compat)."""
        from src.application.use_cases.process_pdf_to_speech import ProcessPdfToSpeechUseCase

        generator = MagicMock()
        processor = MagicMock()
        text_service = MagicMock()
        text_service.chunk_text.return_value = ["chunk one"]

        uc = ProcessPdfToSpeechUseCase(
            extractor=MagicMock(),
            generator=generator,
            processor=processor,
            text_service=text_service,
            cache_repo=None,
        )

        settings = VoiceSettings(voice_id="test-voice", rate="+0%", pitch="+0Hz")
        processor.merge_wavs.return_value = "merged.mp3"
        processor.mix_with_bgm.return_value = "final.mp3"

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = uc.execute(
            text="chunk one",
            pdf_path=str(tmp_path / "test.pdf"),
            output_base_dir=str(output_dir),
            voice_settings=settings,
        )

        generator.generate_speech.assert_called_once()
