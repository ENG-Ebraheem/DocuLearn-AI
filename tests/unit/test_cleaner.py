import pytest
from app.services.text_processing.cleaner import TextCleaner


class TestTextCleaner:

    def test_clean_empty_string(self):
        assert TextCleaner.clean("") == ""

    def test_clean_none_returns_empty(self):
        assert TextCleaner.clean(None) == ""

    def test_normalize_line_breaks(self):
        text = "line1\r\nline2\rline3"
        result = TextCleaner.clean(text)
        assert "\r" not in result
        assert "line1" in result
        assert "line2" in result
        assert "line3" in result

    def test_collapse_whitespace(self):
        text = "word1    word2\t\tword3"
        result = TextCleaner.clean(text)
        assert "    " not in result
        assert "\t\t" not in result
        assert "word1 word2 word3" == result

    def test_limit_consecutive_newlines(self):
        text = "a\n\n\n\n\nb"
        result = TextCleaner.clean(text)
        assert "\n\n\n" not in result
        assert "a" in result
        assert "b" in result

    def test_strip_lines(self):
        text = "   hello   \n   world   "
        result = TextCleaner.clean(text)
        assert result == "hello\nworld"

    def test_clean_preserves_content(self):
        text = "The quick brown fox jumps over the lazy dog."
        result = TextCleaner.clean(text)
        assert result == text

    def test_clean_multiline_paragraph(self):
        text = """
            First paragraph with
            multiple lines.


            Second paragraph.
        """
        result = TextCleaner.clean(text)
        assert "First paragraph with" in result
        assert "multiple lines" in result
        assert "Second paragraph" in result
