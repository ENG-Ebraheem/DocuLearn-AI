import re
from dataclasses import dataclass


@dataclass
class TextQualityMetrics:
    char_count: int
    arabic_ratio: float
    replacement_ratio: float
    suspicious_count: int
    whitespace_anomalies: int
    quality_score: float
    is_poor_quality: bool


class TextQualityAnalyzer:
    """Analyze text quality after extraction.

    Metrics feed into the pipeline so docs with poor OCR
    can be flagged as NEEDS_OCR instead of silently failing
    to produce usable content.
    """

    REPLACEMENT_CHARS = {
        "\ufffd",  # Unicode replacement char
        "?",
        "#",
        "□",
        "■",
    }

    SUSPICIOUS_TOKENS = re.compile(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f]"
    )

    @classmethod
    def analyze(
        cls, text: str, threshold: float = 0.4
    ) -> TextQualityMetrics:
        if not text:
            return TextQualityMetrics(
                char_count=0,
                arabic_ratio=0.0,
                replacement_ratio=0.0,
                suspicious_count=0,
                whitespace_anomalies=0,
                quality_score=0.0,
                is_poor_quality=True,
            )

        char_count = len(text)
        arabic_ratio = cls._arabic_ratio(text)
        replacement_ratio = cls._replacement_ratio(text)
        suspicious_count = len(
            cls.SUSPICIOUS_TOKENS.findall(text)
        )
        whitespace_anomalies = cls._whitespace_anomalies(
            text
        )

        quality_score = cls._compute_score(
            char_count=char_count,
            arabic_ratio=arabic_ratio,
            replacement_ratio=replacement_ratio,
            suspicious_count=suspicious_count,
            whitespace_anomalies=whitespace_anomalies,
        )

        return TextQualityMetrics(
            char_count=char_count,
            arabic_ratio=arabic_ratio,
            replacement_ratio=replacement_ratio,
            suspicious_count=suspicious_count,
            whitespace_anomalies=whitespace_anomalies,
            quality_score=quality_score,
            is_poor_quality=quality_score < threshold,
        )

    @classmethod
    def _arabic_ratio(cls, text: str) -> float:
        total = len(text)
        if total == 0:
            return 0.0
        arabic = sum(
            1
            for c in text
            if "\u0600" <= c <= "\u06ff"
            or "\u0750" <= c <= "\u077f"
            or "\u08a0" <= c <= "\u08ff"
            or "\ufe70" <= c <= "\ufeff"
        )
        return arabic / total

    @classmethod
    def _replacement_ratio(cls, text: str) -> float:
        total = len(text)
        if total == 0:
            return 0.0
        count = sum(
            1
            for c in text
            if c in cls.REPLACEMENT_CHARS
        )
        return count / total

    @classmethod
    def _whitespace_anomalies(cls, text: str) -> int:
        return len(re.findall(r"[ \t]{4,}", text))

    @classmethod
    def _compute_score(
        cls,
        char_count: int,
        arabic_ratio: float,
        replacement_ratio: float,
        suspicious_count: int,
        whitespace_anomalies: int,
    ) -> float:
        score = 1.0

        if char_count < 50:
            score -= 0.3

        if replacement_ratio > 0.05:
            score -= replacement_ratio * 10

        if suspicious_count > 0:
            score -= min(
                suspicious_count * 0.05, 0.3
            )

        if whitespace_anomalies > 5:
            score -= 0.1

        if arabic_ratio > 0.05:
            score += 0.05

        return max(0.0, min(1.0, score))
