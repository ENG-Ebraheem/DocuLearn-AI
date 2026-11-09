import pytest
from app.services.text_processing.quality_analyzer import (
    TextQualityAnalyzer,
)


class TestTextQualityAnalyzer:

    def test_empty_text_poor_quality(self):
        result = TextQualityAnalyzer.analyze("")
        assert result.is_poor_quality
        assert result.char_count == 0

    def test_good_quality_text(self):
        text = (
            "هذا نص عربي طويل يحتوي على معلومات "
            "مهمة حول تعلم الذكاء الاصطناعي. "
            "يستخدم هذا المستند تقنيات متقدمة في "
            "معالجة اللغات الطبيعية."
        )
        result = TextQualityAnalyzer.analyze(text)
        assert not result.is_poor_quality
        assert result.char_count > 0
        assert result.arabic_ratio > 0.3
        assert result.quality_score > 0.4

    def test_replacement_chars_lower_quality(self):
        text = "Hello \ufffd \ufffd \ufffd world"
        result = TextQualityAnalyzer.analyze(text)
        assert result.replacement_ratio > 0
        assert result.quality_score < 1.0

    def test_short_text_penalty(self):
        text = "hi"
        result = TextQualityAnalyzer.analyze(text)
        assert result.quality_score < 0.8

    def test_whitespace_anomalies(self):
        text = "word1     word2     word3     word4     word5     word6"
        result = TextQualityAnalyzer.analyze(text)
        assert result.whitespace_anomalies > 0

    def test_suspicious_control_chars(self):
        text = "Hello\x00World\x01Test"
        result = TextQualityAnalyzer.analyze(text)
        assert result.suspicious_count > 0

    def test_threshold_parameter(self):
        text = "some short text"
        result_pass = TextQualityAnalyzer.analyze(
            text, threshold=0.1
        )
        result_fail = TextQualityAnalyzer.analyze(
            text, threshold=0.9
        )
        assert result_pass.quality_score == (
            result_fail.quality_score
        )
