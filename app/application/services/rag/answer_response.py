from dataclasses import dataclass, field


@dataclass
class Source:
    document_id: str
    document_name: str
    page: int | None
    chunk_id: str
    score: float
    excerpt: str


@dataclass
class AnswerResponse:
    answer: str
    sources: list[Source]
    confidence: float
    model_used: str
    has_sufficient_context: bool
