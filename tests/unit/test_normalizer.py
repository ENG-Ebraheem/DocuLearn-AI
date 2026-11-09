import pytest
from app.services.text_processing.normalizer import (
    ArabicNormalizer,
)


class TestArabicNormalizer:

    def test_normalize_alef_variants(self):
        text = "\u0623\u062b\u0625\u0631\u0622\u0645"
        result = ArabicNormalizer.normalize_search(text)
        assert "\u0627" in result
        assert "\u0623" not in result
        assert "\u0625" not in result
        assert "\u0622" not in result

    def test_normalize_taa_marbuta(self):
        text = "\u0645\u0631\u062d\u0628\u0629"
        result = ArabicNormalizer.normalize_search(text)
        assert "\u0647" in result
        assert "\u0629" not in result

    def test_normalize_alef_maqsura(self):
        text = "\u0639\u0644\u0649"
        result = ArabicNormalizer.normalize_search(text)
        assert "\u064a" in result
        assert "\u0649" not in result

    def test_remove_diacritics(self):
        text = "\u0627\u0644\u0642\u064f\u0631\u064e\u0622\u0646"
        result = ArabicNormalizer.normalize_search(text)
        assert "\u064f" not in result
        assert "\u064e" not in result

    def test_remove_tatweel(self):
        text = "\u0627\u0644\u0642\u0640\u0631\u0622\u0646"
        result = ArabicNormalizer.normalize_search(text)
        assert "\u0640" not in result

    def test_normalize_whitespace(self):
        text = "hello  \t  world"
        result = ArabicNormalizer.normalize_search(text)
        assert "  " not in result
        assert "\t" not in result

    def test_empty_text(self):
        assert ArabicNormalizer.normalize_search("") == ""
        assert ArabicNormalizer.normalize_search(None) == ""

    def test_is_arabic_dominant(self):
        assert ArabicNormalizer.is_arabic_dominant(
            "مرحبا بكم في هذا المستند"
        )
        assert not ArabicNormalizer.is_arabic_dominant(
            "Hello world"
        )

    def test_detect_language_arabic(self):
        assert (
            ArabicNormalizer.detect_language(
                "مرحبا بكم في هذا المستند التعليمي"
            )
            == "ar"
        )

    def test_detect_language_english(self):
        assert (
            ArabicNormalizer.detect_language(
                "Hello world, this is a test document"
            )
            == "en"
        )

    def test_detect_language_mixed(self):
        assert (
            ArabicNormalizer.detect_language(
                "مرحبا world في هذا test"
            )
            == "mixed"
        )

    def test_preserves_numbers(self):
        text = "الصفحة 123 من 456"
        result = ArabicNormalizer.normalize_search(text)
        assert "123" in result
        assert "456" in result
