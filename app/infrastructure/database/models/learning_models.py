import json
from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.database import Base


class LearningSummaryModel(Base):
    __tablename__ = "learning_summaries"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    document_id: Mapped[str] = mapped_column(
        String(32), index=True
    )
    title: Mapped[str] = mapped_column(
        Text, default=""
    )
    overview: Mapped[str] = mapped_column(
        Text, default=""
    )
    extra_json: Mapped[str] = mapped_column(
        Text, default="{}", name="metadata_json"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def extra_metadata(self) -> dict:
        return json.loads(self.extra_json)

    @extra_metadata.setter
    def extra_metadata(self, value: dict) -> None:
        self.extra_json = json.dumps(value)


class KeyConceptModel(Base):
    __tablename__ = "key_concepts"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    document_id: Mapped[str] = mapped_column(
        String(32), index=True
    )
    term: Mapped[str] = mapped_column(Text, default="")
    definition: Mapped[str] = mapped_column(
        Text, default=""
    )
    extra_json: Mapped[str] = mapped_column(
        Text, default="{}", name="metadata_json"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def extra_metadata(self) -> dict:
        return json.loads(self.extra_json)

    @extra_metadata.setter
    def extra_metadata(self, value: dict) -> None:
        self.extra_json = json.dumps(value)


class QuestionModel(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    document_id: Mapped[str] = mapped_column(
        String(32), index=True
    )
    question_text: Mapped[str] = mapped_column(
        Text, default=""
    )
    answer: Mapped[str] = mapped_column(
        Text, default=""
    )
    difficulty: Mapped[str] = mapped_column(
        String(20), default="MEDIUM"
    )
    question_type: Mapped[str] = mapped_column(
        String(30), default="UNDERSTANDING"
    )
    extra_json: Mapped[str] = mapped_column(
        Text, default="{}", name="metadata_json"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def extra_metadata(self) -> dict:
        return json.loads(self.extra_json)

    @extra_metadata.setter
    def extra_metadata(self, value: dict) -> None:
        self.extra_json = json.dumps(value)


class QuizModel(Base):
    __tablename__ = "quizzes"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    document_id: Mapped[str] = mapped_column(
        String(32), index=True
    )
    title: Mapped[str] = mapped_column(
        Text, default=""
    )
    description: Mapped[str] = mapped_column(
        Text, default=""
    )
    extra_json: Mapped[str] = mapped_column(
        Text, default="{}", name="metadata_json"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def extra_metadata(self) -> dict:
        return json.loads(self.extra_json)

    @extra_metadata.setter
    def extra_metadata(self, value: dict) -> None:
        self.extra_json = json.dumps(value)


class QuizQuestionModel(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    quiz_id: Mapped[str] = mapped_column(
        String(32), index=True
    )
    question_text: Mapped[str] = mapped_column(
        Text, default=""
    )
    question_type: Mapped[str] = mapped_column(
        String(30), default="MCQ"
    )
    correct_answer: Mapped[str] = mapped_column(
        Text, default=""
    )
    explanation: Mapped[str] = mapped_column(
        Text, default=""
    )
    order_index: Mapped[int] = mapped_column(
        Integer, default=0
    )
    extra_json: Mapped[str] = mapped_column(
        Text, default="{}", name="metadata_json"
    )

    @property
    def extra_metadata(self) -> dict:
        return json.loads(self.extra_json)

    @extra_metadata.setter
    def extra_metadata(self, value: dict) -> None:
        self.extra_json = json.dumps(value)


class QuizSessionModel(Base):
    __tablename__ = "quiz_sessions"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    quiz_id: Mapped[str] = mapped_column(
        String(32), index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="in_progress"
    )
    score: Mapped[int] = mapped_column(
        Integer, default=0
    )
    percentage: Mapped[float] = mapped_column(
        Float, default=0.0
    )

    @property
    def extra_metadata(self) -> dict:
        return {}

    @extra_metadata.setter
    def extra_metadata(self, value: dict) -> None:
        pass


class QuizAnswerModel(Base):
    __tablename__ = "quiz_answers"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    session_id: Mapped[str] = mapped_column(
        String(32), index=True
    )
    quiz_question_id: Mapped[str] = mapped_column(
        String(32), index=True
    )
    user_answer: Mapped[str] = mapped_column(
        Text, default=""
    )
    is_correct: Mapped[bool] = mapped_column(
        default=False
    )
    answered_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )


class FlashcardModel(Base):
    __tablename__ = "flashcards"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    document_id: Mapped[str] = mapped_column(
        String(32), index=True
    )
    front: Mapped[str] = mapped_column(
        Text, default=""
    )
    back: Mapped[str] = mapped_column(
        Text, default=""
    )
    extra_json: Mapped[str] = mapped_column(
        Text, default="{}", name="metadata_json"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def extra_metadata(self) -> dict:
        return json.loads(self.extra_json)

    @extra_metadata.setter
    def extra_metadata(self, value: dict) -> None:
        self.extra_json = json.dumps(value)


class FlashcardReviewModel(Base):
    __tablename__ = "flashcard_reviews"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    flashcard_id: Mapped[str] = mapped_column(
        String(32), index=True
    )
    rating: Mapped[str] = mapped_column(
        String(20), default="GOOD"
    )
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )


class TopicModel(Base):
    __tablename__ = "topics"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True
    )
    document_id: Mapped[str] = mapped_column(
        String(32), index=True
    )
    name: Mapped[str] = mapped_column(
        String(255), default=""
    )
    description: Mapped[str] = mapped_column(
        Text, default=""
    )
