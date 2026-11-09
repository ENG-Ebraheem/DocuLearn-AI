from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


@dataclass
class LearningSummary:
    id: str = field(
        default_factory=lambda: uuid4().hex
    )
    document_id: str = ""
    title: str = ""
    overview: str = ""
    sections: list = field(default_factory=list)
    key_takeaways: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    summary_length: str = "medium"
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class KeyConcept:
    id: str = field(
        default_factory=lambda: uuid4().hex
    )
    document_id: str = ""
    term: str = ""
    definition: str = ""
    explanation: str = ""
    importance: str = ""
    topic: str = ""
    sources: list = field(default_factory=list)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class Question:
    id: str = field(
        default_factory=lambda: uuid4().hex
    )
    document_id: str = ""
    question: str = ""
    answer: str = ""
    difficulty: str = "MEDIUM"
    question_type: str = "UNDERSTANDING"
    topic: str = ""
    sources: list = field(default_factory=list)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class Quiz:
    id: str = field(
        default_factory=lambda: uuid4().hex
    )
    document_id: str = ""
    title: str = ""
    description: str = ""
    difficulty: str = "MEDIUM"
    question_types: list = field(default_factory=list)
    number_of_questions: int = 5
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class QuizQuestion:
    id: str = field(
        default_factory=lambda: uuid4().hex
    )
    quiz_id: str = ""
    question: str = ""
    question_type: str = "MCQ"
    options: list = field(default_factory=list)
    correct_answer: str = ""
    explanation: str = ""
    difficulty: str = "MEDIUM"
    topic: str = ""
    sources: list = field(default_factory=list)
    order_index: int = 0


@dataclass
class QuizSession:
    id: str = field(
        default_factory=lambda: uuid4().hex
    )
    quiz_id: str = ""
    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: Optional[datetime] = None
    status: str = "in_progress"
    score: int = 0
    percentage: float = 0.0


@dataclass
class QuizAnswer:
    id: str = field(
        default_factory=lambda: uuid4().hex
    )
    session_id: str = ""
    quiz_question_id: str = ""
    user_answer: str = ""
    is_correct: bool = False
    answered_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class Flashcard:
    id: str = field(
        default_factory=lambda: uuid4().hex
    )
    document_id: str = ""
    front: str = ""
    back: str = ""
    topic: str = ""
    sources: list = field(default_factory=list)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class FlashcardReview:
    id: str = field(
        default_factory=lambda: uuid4().hex
    )
    flashcard_id: str = ""
    rating: str = "GOOD"
    reviewed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class Topic:
    id: str = field(
        default_factory=lambda: uuid4().hex
    )
    document_id: str = ""
    name: str = ""
    description: str = ""
