import pytest
import json
from app.application.services.learning.generate_summary import (
    GenerateSummaryUseCase,
)
from app.application.services.learning.generate_key_concepts import (
    GenerateKeyConceptsUseCase,
)
from app.application.services.learning.generate_questions import (
    GenerateQuestionsUseCase,
)
from app.application.services.learning.generate_quiz import (
    GenerateQuizUseCase,
)
from app.application.services.learning.generate_flashcards import (
    GenerateFlashcardsUseCase,
)
from app.application.services.learning.quiz_scoring import (
    QuizScoringService,
)
from app.infrastructure.llm.fake_llm_provider import (
    FakeLLMProvider,
)
from app.infrastructure.embeddings.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from app.infrastructure.vector_store.faiss_vector_store import (
    FAISSVectorStore,
)
from app.infrastructure.database.database import (
    Base,
    engine,
    SessionLocal,
)
from app.infrastructure.database.repositories.learning_summary_repository_impl import (
    LearningSummaryRepositoryImpl,
)
from app.infrastructure.database.repositories.key_concept_repository_impl import (
    KeyConceptRepositoryImpl,
)
from app.infrastructure.database.repositories.question_repository_impl import (
    QuestionRepositoryImpl,
)
from app.infrastructure.database.repositories.quiz_repository_impl import (
    QuizRepositoryImpl,
)
from app.application.services.rag.retriever import (
    Retriever,
)
from app.application.services.rag.context_builder import (
    ContextBuilder,
)
from app.domain.entities.chunk import Chunk
from app.domain.entities.learning import (
    QuizSession,
    QuizAnswer,
    Flashcard,
)


@pytest.fixture(autouse=True)
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def deps():
    provider = SentenceTransformerEmbeddingProvider()
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        store = FAISSVectorStore(
            dimension=provider.dimension,
            store_path=tmpdir,
        )

        chunks = [
            Chunk(
                id="c1", document_id="d1",
                content="Machine learning is a subset of AI that learns from data.",
                chunk_index=0,
                metadata={"document_name": "ai.pdf", "document_id": "d1", "page": 1},
            ),
            Chunk(
                id="c2", document_id="d1",
                content="Neural networks are inspired by biological brain structure.",
                chunk_index=1,
                metadata={"document_name": "ai.pdf", "document_id": "d1", "page": 2},
            ),
        ]
        embeddings = provider.embed_documents([c.content for c in chunks])
        store.add(chunks, embeddings)

        yield {
            "provider": provider,
            "store": store,
            "retriever": Retriever(
                embedding_provider=provider,
                vector_store=store,
            ),
            "context_builder": ContextBuilder(),
        }


def _make_summary_uc(llm_response, session):
    llm = FakeLLMProvider(response=llm_response)
    return GenerateSummaryUseCase(
        retriever=None,
        context_builder=ContextBuilder(),
        llm_provider=llm,
        summary_repo=LearningSummaryRepositoryImpl(session),
    ), llm


def _make_concepts_uc(llm_response, session):
    llm = FakeLLMProvider(response=llm_response)
    return GenerateKeyConceptsUseCase(
        retriever=None,
        context_builder=ContextBuilder(),
        llm_provider=llm,
        concept_repo=KeyConceptRepositoryImpl(session),
    ), llm


def _make_questions_uc(llm_response, session):
    llm = FakeLLMProvider(response=llm_response)
    return GenerateQuestionsUseCase(
        retriever=None,
        context_builder=ContextBuilder(),
        llm_provider=llm,
        question_repo=QuestionRepositoryImpl(session),
    ), llm


def _make_quiz_uc(llm_response, session):
    llm = FakeLLMProvider(response=llm_response)
    return GenerateQuizUseCase(
        retriever=None,
        context_builder=ContextBuilder(),
        llm_provider=llm,
        quiz_repo=QuizRepositoryImpl(session),
    ), llm


class TestGenerateSummary:

    def test_generates_and_persists(self, deps, db):
        response = json.dumps({
            "title": "مقدمة في الذكاء الاصطناعي",
            "overview": "ملخص شامل",
            "sections": [{"title": "قسم", "content": "محتوى"}],
            "key_takeaways": ["نقطة 1"],
        }, ensure_ascii=False)

        uc = GenerateSummaryUseCase(
            retriever=deps["retriever"],
            context_builder=deps["context_builder"],
            llm_provider=FakeLLMProvider(response=response),
            summary_repo=LearningSummaryRepositoryImpl(db),
        )

        summary = uc.execute("d1")
        assert summary.title == "مقدمة في الذكاء الاصطناعي"
        assert summary.overview == "ملخص شامل"
        assert len(summary.sections) == 1
        assert len(summary.key_takeaways) == 1
        assert summary.document_id == "d1"

    def test_caching_returns_existing(self, deps, db):
        response = json.dumps({
            "title": "test", "overview": "overview",
            "sections": [], "key_takeaways": [],
        }, ensure_ascii=False)

        repo = LearningSummaryRepositoryImpl(db)
        uc = GenerateSummaryUseCase(
            retriever=deps["retriever"],
            context_builder=deps["context_builder"],
            llm_provider=FakeLLMProvider(response=response),
            summary_repo=repo,
        )

        s1 = uc.execute("d1")
        s2 = uc.execute("d1")
        assert s1.id == s2.id

    def test_regenerate(self, deps, db):
        response1 = json.dumps({
            "title": "v1", "overview": "o1",
            "sections": [], "key_takeaways": [],
        }, ensure_ascii=False)
        response2 = json.dumps({
            "title": "v2", "overview": "o2",
            "sections": [], "key_takeaways": [],
        }, ensure_ascii=False)

        repo = LearningSummaryRepositoryImpl(db)

        uc1 = GenerateSummaryUseCase(
            retriever=deps["retriever"],
            context_builder=deps["context_builder"],
            llm_provider=FakeLLMProvider(response=response1),
            summary_repo=repo,
        )
        uc1.execute("d1")

        repo.delete_by_document_id("d1")

        uc2 = GenerateSummaryUseCase(
            retriever=deps["retriever"],
            context_builder=deps["context_builder"],
            llm_provider=FakeLLMProvider(response=response2),
            summary_repo=repo,
        )
        s2 = uc2.execute("d1")
        assert s2.title == "v2"


class TestGenerateKeyConcepts:

    def test_generates_and_persists(self, deps, db):
        response = json.dumps([
            {
                "term": "التعلم الآلي",
                "definition": "فنية تعلم من البيانات",
                "explanation": "شرح تفصيلي",
                "importance": "أساسية",
                "topic": "AI",
            },
        ], ensure_ascii=False)

        uc = GenerateKeyConceptsUseCase(
            retriever=deps["retriever"],
            context_builder=deps["context_builder"],
            llm_provider=FakeLLMProvider(response=response),
            concept_repo=KeyConceptRepositoryImpl(db),
        )

        concepts = uc.execute("d1")
        assert len(concepts) == 1
        assert concepts[0].term == "التعلم الآلي"

    def test_caching(self, deps, db):
        response = json.dumps([
            {"term": "x", "definition": "y",
             "explanation": "", "importance": "", "topic": ""},
        ], ensure_ascii=False)

        repo = KeyConceptRepositoryImpl(db)
        uc = GenerateKeyConceptsUseCase(
            retriever=deps["retriever"],
            context_builder=deps["context_builder"],
            llm_provider=FakeLLMProvider(response=response),
            concept_repo=repo,
        )

        c1 = uc.execute("d1")
        c2 = uc.execute("d1")
        assert len(c1) == len(c2)


class TestGenerateQuestions:

    def test_generates_and_persists(self, deps, db):
        response = json.dumps([
            {
                "question": "ما هو التعلم الآلي؟",
                "answer": "فرع من الذكاء الاصطناعي",
                "difficulty": "EASY",
                "question_type": "DEFINITION",
                "topic": "ML",
            },
        ], ensure_ascii=False)

        uc = GenerateQuestionsUseCase(
            retriever=deps["retriever"],
            context_builder=deps["context_builder"],
            llm_provider=FakeLLMProvider(response=response),
            question_repo=QuestionRepositoryImpl(db),
        )

        questions = uc.execute("d1")
        assert len(questions) == 1
        assert questions[0].difficulty == "EASY"

    def test_validates_question_and_answer(self, deps, db):
        response = json.dumps([
            {"question": "", "answer": "x"},
            {"question": "Q", "answer": ""},
            {"question": "Good", "answer": "Good"},
        ], ensure_ascii=False)

        uc = GenerateQuestionsUseCase(
            retriever=deps["retriever"],
            context_builder=deps["context_builder"],
            llm_provider=FakeLLMProvider(response=response),
            question_repo=QuestionRepositoryImpl(db),
        )

        questions = uc.execute("d1")
        assert len(questions) == 1
        assert questions[0].question == "Good"


class TestGenerateQuiz:

    def test_generates_quiz_with_questions(self, deps, db):
        response = json.dumps({
            "title": "اختبار AI",
            "description": "اختبار شامل",
            "questions": [
                {
                    "question": "Q1",
                    "type": "MCQ",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "لأن A صحيح",
                    "difficulty": "EASY",
                    "topic": "AI",
                },
            ],
        }, ensure_ascii=False)

        uc = GenerateQuizUseCase(
            retriever=deps["retriever"],
            context_builder=deps["context_builder"],
            llm_provider=FakeLLMProvider(response=response),
            quiz_repo=QuizRepositoryImpl(db),
        )

        quiz = uc.execute("d1")
        assert quiz.title == "اختبار AI"

        repo = QuizRepositoryImpl(db)
        questions = repo.find_questions_by_quiz_id(quiz.id)
        assert len(questions) == 1
        assert questions[0].correct_answer == "A"


class TestQuizScoring:

    def test_scoring_correct_and_incorrect(self, deps, db):
        from app.domain.entities.learning import (
            Quiz, QuizQuestion,
        )

        repo = QuizRepositoryImpl(db)
        quiz = repo.save_quiz(
            Quiz(document_id="d1", title="Test")
        )
        q1 = repo.save_question(
            QuizQuestion(
                quiz_id=quiz.id,
                question="Q1",
                options=["A", "B"],
                correct_answer="A",
                order_index=0,
            )
        )
        q2 = repo.save_question(
            QuizQuestion(
                quiz_id=quiz.id,
                question="Q2",
                options=["X", "Y"],
                correct_answer="X",
                order_index=1,
            )
        )

        session = repo.save_session(
            QuizSession(quiz_id=quiz.id)
        )

        scoring = QuizScoringService(quiz_repo=repo)
        result = scoring.submit_session(
            session_id=session.id,
            answers=[
                {"quiz_question_id": q1.id, "user_answer": "A"},
                {"quiz_question_id": q2.id, "user_answer": "Y"},
            ],
        )

        assert result.score == 1
        assert result.percentage == 50.0
        assert result.status == "completed"

    def test_get_results(self, deps, db):
        from app.domain.entities.learning import (
            Quiz, QuizQuestion,
        )

        repo = QuizRepositoryImpl(db)
        quiz = repo.save_quiz(
            Quiz(document_id="d1", title="Test")
        )
        q1 = repo.save_question(
            QuizQuestion(
                quiz_id=quiz.id,
                question="Q1",
                options=["A", "B"],
                correct_answer="A",
                explanation="A هو الصحيح",
                order_index=0,
            )
        )

        session = repo.save_session(
            QuizSession(quiz_id=quiz.id)
        )

        scoring = QuizScoringService(quiz_repo=repo)
        scoring.submit_session(
            session_id=session.id,
            answers=[
                {"quiz_question_id": q1.id, "user_answer": "B"},
            ],
        )

        results = scoring.get_results(session.id)
        assert results["score"] == 0
        assert results["total"] == 1
        assert len(results["answers"]) == 1
        assert not results["answers"][0]["is_correct"]
        assert results["answers"][0]["correct_answer"] == "A"


class TestDocumentDeletion:

    def test_delete_cleans_learning_data(self, deps, db):
        from app.domain.entities.learning import (
            KeyConcept, Flashcard,
        )
        from app.infrastructure.database.repositories.key_concept_repository_impl import (
            KeyConceptRepositoryImpl,
        )
        from app.infrastructure.database.repositories.learning_summary_repository_impl import (
            LearningSummaryRepositoryImpl,
        )
        from app.infrastructure.database.repositories.flashcard_repository_impl import (
            FlashcardRepositoryImpl,
        )

        summary_repo = LearningSummaryRepositoryImpl(db)
        concept_repo = KeyConceptRepositoryImpl(db)
        flashcard_repo = FlashcardRepositoryImpl(db)
        quiz_repo = QuizRepositoryImpl(db)

        summary_repo.save(
            __import__(
                "app.domain.entities.learning",
                fromlist=["LearningSummary"],
            ).LearningSummary(
                document_id="d1", title="Test"
            )
        )
        concept_repo.save_many([
            KeyConcept(
                document_id="d1",
                term="T",
                definition="D",
            )
        ])
        flashcard_repo.save_many([
            Flashcard(
                document_id="d1",
                front="F",
                back="B",
            )
        ])

        assert summary_repo.find_by_document_id("d1") is not None
        assert len(concept_repo.find_by_document_id("d1")) == 1
        assert len(flashcard_repo.find_by_document_id("d1")) == 1

        summary_repo.delete_by_document_id("d1")
        concept_repo.delete_by_document_id("d1")
        flashcard_repo.delete_by_document_id("d1")

        assert summary_repo.find_by_document_id("d1") is None
        assert len(concept_repo.find_by_document_id("d1")) == 0
        assert len(flashcard_repo.find_by_document_id("d1")) == 0
