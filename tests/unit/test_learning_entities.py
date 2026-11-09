import pytest
from app.domain.entities.learning import (
    LearningSummary,
    KeyConcept,
    Question,
    Quiz,
    QuizQuestion,
    QuizSession,
    QuizAnswer,
    Flashcard,
    FlashcardReview,
    Topic,
)


class TestLearningEntities:

    def test_learning_summary_defaults(self):
        s = LearningSummary()
        assert s.document_id == ""
        assert s.title == ""
        assert s.sections == []
        assert s.key_takeaways == []
        assert s.summary_length == "medium"
        assert s.id

    def test_key_concept_defaults(self):
        c = KeyConcept()
        assert c.document_id == ""
        assert c.term == ""
        assert c.definition == ""
        assert c.explanation == ""
        assert c.importance == ""
        assert c.sources == []

    def test_question_defaults(self):
        q = Question()
        assert q.difficulty == "MEDIUM"
        assert q.question_type == "UNDERSTANDING"
        assert q.question == ""
        assert q.answer == ""

    def test_quiz_defaults(self):
        quiz = Quiz()
        assert quiz.difficulty == "MEDIUM"
        assert quiz.number_of_questions == 5
        assert quiz.question_types == []

    def test_quiz_question_defaults(self):
        qq = QuizQuestion()
        assert qq.question_type == "MCQ"
        assert qq.options == []
        assert qq.order_index == 0

    def test_quiz_session_defaults(self):
        qs = QuizSession()
        assert qs.status == "in_progress"
        assert qs.score == 0
        assert qs.percentage == 0.0
        assert qs.completed_at is None

    def test_quiz_answer_defaults(self):
        qa = QuizAnswer()
        assert qa.user_answer == ""
        assert qa.is_correct is False

    def test_flashcard_defaults(self):
        fc = Flashcard()
        assert fc.front == ""
        assert fc.back == ""
        assert fc.topic == ""
        assert fc.sources == []

    def test_flashcard_review_defaults(self):
        fr = FlashcardReview()
        assert fr.rating == "GOOD"
        assert fr.flashcard_id == ""

    def test_topic_defaults(self):
        t = Topic()
        assert t.name == ""
        assert t.description == ""
        assert t.document_id == ""

    def test_all_entities_have_ids(self):
        entities = [
            LearningSummary(), KeyConcept(), Question(),
            Quiz(), QuizQuestion(), QuizSession(),
            QuizAnswer(), Flashcard(), FlashcardReview(),
            Topic(),
        ]
        for e in entities:
            assert e.id
            assert len(e.id) == 32
