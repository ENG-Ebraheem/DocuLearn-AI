import re


class ArabicNormalizer:
    """Normalize Arabic text for search and embedding.

    Preserves original text for citations. Use normalize_search()
    for query/indexing normalization only.
    """

    ALEF_MAP = {
        "\u0623": "\u0627",
        "\u0622": "\u0627",
        "\u0625": "\u0627",
    }

    TAA_MARBUTA = "\u0629"
    TAA_MAFTUHA = "\u0647"

    ALEF_MAQSURA = "\u0649"
    YAA = "\u064a"

    DIACRITICS = re.compile(
        "[\u0617-\u061a\u064b-\u065f\u0670]"
    )

    WHITESPACE = re.compile(r"[\u200b\u200c\u200d\ufeff]")
    REPEATED_DOTS = re.compile(r"[.…]{3,}")

    @classmethod
    def normalize_search(cls, text: str) -> str:
        """Normalize text for search/embedding indexing."""
        if not text:
            return ""

        text = text.strip()
        text = cls._normalize_unicode(text)
        text = cls._remove_diacritics(text)
        text = cls._normalize_alef(text)
        text = cls._normalize_taa_marbuta(text)
        text = cls._normalize_alef_maqsura(text)
        text = cls._normalize_tatweel(text)
        text = cls._normalize_whitespace(text)
        text = cls._normalize_punctuation(text)
        return text

    @classmethod
    def is_arabic_dominant(cls, text: str) -> bool:
        """Check if text is predominantly Arabic."""
        if not text:
            return False
        arabic = sum(
            1
            for c in text
            if "\u0600" <= c <= "\u06ff"
            or "\u0750" <= c <= "\u077f"
            or "\u08a0" <= c <= "\u08ff"
            or "\ufe70" <= c <= "\ufeff"
        )
        total = len(text.replace(" ", "").replace("\n", ""))
        return total > 0 and (arabic / total) > 0.3

    @classmethod
    def detect_language(cls, text: str) -> str:
        """Detect dominant language: 'ar', 'en', or 'mixed'."""
        if not text:
            return "en"
        arabic = sum(
            1
            for c in text
            if "\u0600" <= c <= "\u06ff"
            or "\u0750" <= c <= "\u077f"
            or "\u08a0" <= c <= "\u08ff"
            or "\ufe70" <= c <= "\ufeff"
        )
        latin = sum(
            1
            for c in text
            if ("a" <= c.lower() <= "z")
            or ("0" <= c <= "9")
        )
        total = arabic + latin
        if total == 0:
            return "en"
        ratio = arabic / total
        if ratio > 0.6:
            return "ar"
        if ratio < 0.2:
            return "en"
        return "mixed"

    @classmethod
    def _normalize_unicode(cls, text: str) -> str:
        text = cls.WHITESPACE.sub(" ", text)
        return text

    @classmethod
    def _remove_diacritics(cls, text: str) -> str:
        return cls.DIACRITICS.sub("", text)

    @classmethod
    def _normalize_alef(cls, text: str) -> str:
        for char, replacement in cls.ALEF_MAP.items():
            text = text.replace(char, replacement)
        return text

    @classmethod
    def _normalize_taa_marbuta(cls, text: str) -> str:
        return text.replace(
            cls.TAA_MARBUTA, cls.TAA_MAFTUHA
        )

    @classmethod
    def _normalize_alef_maqsura(cls, text: str) -> str:
        return text.replace(
            cls.ALEF_MAQSURA, cls.YAA
        )

    @classmethod
    def _normalize_tatweel(cls, text: str) -> str:
        return text.replace("\u0640", "")

    @classmethod
    def _normalize_whitespace(cls, text: str) -> str:
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @classmethod
    def _normalize_punctuation(cls, text: str) -> str:
        text = cls.REPEATED_DOTS.sub("...", text)
        return text
