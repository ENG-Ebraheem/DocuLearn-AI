import pytest
from app.services.text_processing.normalizer import ArabicNormalizer


class TestArabicNormalizer:

    def test_normalize_diacritics(self):
        text = "\u0627\u0644\u0630\u064e\u0651\u0643\u064e\u0627\u0621\u064f \u0627\u0644\u0625\u0650\u0635\u0652\u0637\u0650\u0646\u064e\u0627\u0639\u0650\u064a\u064f\u0651"
        normalized = ArabicNormalizer.normalize_search(text)
        assert "\u0627\u0644\u0630\u0643\u0627\u0621" in normalized

    def test_normalize_alef(self):
        assert ArabicNormalizer.normalize_search("\u0623\u062d\u0645\u062f") == "\u0627\u062d\u0645\u062f"
        assert ArabicNormalizer.normalize_search("\u0625\u0628\u0631\u0627\u0647\u064a\u0645") == "\u0627\u0628\u0631\u0627\u0647\u064a\u0645"
        assert ArabicNormalizer.normalize_search("\u0622\u0644\u0629") == "\u0627\u0644\u0647"

    def test_normalize_taa_marbuta_and_maqsura(self):
        assert ArabicNormalizer.normalize_search("\u0645\u0643\u062a\u0629") == "\u0645\u0643\u062a\u0647"
        assert ArabicNormalizer.normalize_search("\u0645\u0633\u062a\u0634\u0641\u0649") == "\u0645\u0633\u062a\u0634\u0641\u064a"

    def test_detect_language(self):
        assert ArabicNormalizer.detect_language("\u0645\u0631\u062d\u0628\u0627 \u0628\u0643") == "ar"
        assert ArabicNormalizer.detect_language("Hello World 123") == "en"

    def test_is_arabic_dominant(self):
        assert ArabicNormalizer.is_arabic_dominant("\u0647\u0630\u0627 \u0627\u0644\u0646\u0635 \u0639\u0631\u0628\u064a") is True
        assert ArabicNormalizer.is_arabic_dominant("This is english text") is False
