import pytest
import json
import tempfile

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
from app.infrastructure.database.repositories.flashcard_repository_impl import (
    FlashcardRepositoryImpl,
)
from app.application.services.rag.retriever import (
    Retriever,
)
from app.application.services.rag.context_builder import (
    ContextBuilder,
)
from app.application.services.learning import (
    GenerateSummaryUseCase,
    GenerateKeyConceptsUseCase,
    GenerateQuestionsUseCase,
    GenerateQuizUseCase,
    QuizScoringService,
    GenerateFlashcardsUseCase,
)
from app.domain.entities.chunk import Chunk
from app.domain.entities.learning import (
    Quiz,
    QuizQuestion,
    QuizSession,
)


@pytest.fixture(autouse=True)
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


class TestLearningEngineIntegration:

    def test_full_flow_summary_concepts_quiz(
        self, db
    ):
        provider = (
            SentenceTransformerEmbeddingProvider()
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            store = FAISSVectorStore(
                dimension=provider.dimension,
                store_path=tmpdir,
            )

            chunks = [
                Chunk(
                    id="c1",
                    document_id="doc1",
                    content=(
                        "Machine learning is a branch of "
                        "AI that enables systems to learn "
                        "from data. Deep learning uses "
                        "neural networks with many layers."
                    ),
                    chunk_index=0,
                    metadata={
                        "document_name": "ai_intro.pdf",
                        "document_id": "doc1",
                        "page": 1,
                    },
                ),
                Chunk(
                    id="c2",
                    document_id="doc1",
                    content=(
                        "Supervised learning uses labeled "
                        "data. Unsupervised learning finds "
                        "patterns in unlabeled data."
                    ),
                    chunk_index=1,
                    metadata={
                        "document_name": "ai_intro.pdf",
                        "document_id": "doc1",
                        "page": 2,
                    },
                ),
            ]

            embeddings = provider.embed_documents(
                [c.content for c in chunks]
            )
            store.add(chunks, embeddings)

            retriever = Retriever(
                embedding_provider=provider,
                vector_store=store,
            )
            context_builder = ContextBuilder()

            summary_llm = FakeLLMProvider(
                response=json.dumps(
                    {
                        "title": "مقدمة في الذكاء الاصطناعي",
                        "overview": "ملخص عن التعلم الآلي والعميق",
                        "sections": [
                            {
                                "title": "التعلم الآلي",
                                "content": "فرع من الذكاء الاصطناعي",
                            }
                        ],
                        "key_takeaways": [
                            "التعلم الآلي يتعلم من البيانات"
                        ],
                    },
                    ensure_ascii=False,
                )
            )

            summary_uc = GenerateSummaryUseCase(
                retriever=retriever,
                context_builder=context_builder,
                llm_provider=summary_llm,
                summary_repo=LearningSummaryRepositoryImpl(
                    db
                ),
            )

            summary = summary_uc.execute("doc1")
            assert summary.title == "مقدمة في الذكاء الاصطناعي"
            assert len(summary.sections) == 1
            assert len(summary.key_takeaways) == 1
            assert summary_llm.call_count == 1

            summary_cached = summary_uc.execute("doc1")
            assert summary_cached.id == summary.id
            assert summary_llm.call_count == 1

            concepts_llm = FakeLLMProvider(
                response=json.dumps(
                    [
                        {
                            "term": "التعلم الآلي",
                            "definition": "تقنية تعلم من البيانات",
                            "explanation": "شرح مفصل",
                            "importance": "أساسية في AI",
                            "topic": "ML",
                        },
                    ],
                    ensure_ascii=False,
                )
            )

            concepts_uc = GenerateKeyConceptsUseCase(
                retriever=retriever,
                context_builder=context_builder,
                llm_provider=concepts_llm,
                concept_repo=KeyConceptRepositoryImpl(
                    db
                ),
            )

            concepts = concepts_uc.execute("doc1")
            assert len(concepts) == 1
            assert concepts[0].term == "التعلم الآلي"

            quiz_llm = FakeLLMProvider(
                response=json.dumps(
                    {
                        "title": "اختبار AI",
                        "description": "اختبار شامل",
                        "questions": [
                            {
                                "question": "ما هو التعلم الآلي؟",
                                "type": "MCQ",
                                "options": [
                                    "فرع من AI",
                                    "نوع من القواعد",
                                    "لغة برمجة",
                                    "نظام تشغيل",
                                ],
                                "correct_answer": "فرع من AI",
                                "explanation": "التعلم الآلي فرع من الذكاء الاصطناعي",
                                "difficulty": "EASY",
                                "topic": "ML",
                            },
                            {
                                "question": "التعلم العميق يستخدم الشبكات العصبية.",
                                "type": "TRUE_FALSE",
                                "options": [
                                    "صحيح",
                                    "خاطئ",
                                ],
                                "correct_answer": "صحيح",
                                "explanation": " صحيح، يستخدم شبكات عصبية متعددة الطبقات",
                                "difficulty": "EASY",
                                "topic": "DL",
                            },
                        ],
                    },
                    ensure_ascii=False,
                )
            )

            quiz_uc = GenerateQuizUseCase(
                retriever=retriever,
                context_builder=context_builder,
                llm_provider=quiz_llm,
                quiz_repo=QuizRepositoryImpl(db),
            )

            quiz = quiz_uc.execute(
                "doc1",
                number_of_questions=2,
            )
            assert quiz.title == "اختبار AI"

            quiz_repo = QuizRepositoryImpl(db)
            questions = (
                quiz_repo.find_questions_by_quiz_id(
                    quiz.id
                )
            )
            assert len(questions) == 2

            session = quiz_repo.save_session(
                QuizSession(quiz_id=quiz.id)
            )

            scoring = QuizScoringService(
                quiz_repo=quiz_repo
            )
            result = scoring.submit_session(
                session_id=session.id,
                answers=[
                    {
                        "quiz_question_id": questions[0].id,
                        "user_answer": "فرع من AI",
                    },
                    {
                        "quiz_question_id": questions[1].id,
                        "user_answer": "خاطئ",
                    },
                ],
            )

            assert result.score == 1
            assert result.percentage == 50.0

            results = scoring.get_results(session.id)
            assert results["total"] == 2
            assert len(results["answers"]) == 2

            flashcard_llm = FakeLLMProvider(
                response=json.dumps(
                    [
                        {
                            "front": "ما هو ML؟",
                            "back": "تعلم من البيانات",
                            "topic": "ML",
                        },
                        {
                            "front": "ما هو DL؟",
                            "back": "شبكات عصبية",
                            "topic": "DL",
                        },
                    ],
                    ensure_ascii=False,
                )
            )

            fc_uc = GenerateFlashcardsUseCase(
                retriever=retriever,
                context_builder=context_builder,
                llm_provider=flashcard_llm,
                flashcard_repo=FlashcardRepositoryImpl(
                    db
                ),
            )

            flashcards = fc_uc.execute("doc1")
            assert len(flashcards) == 2
            assert flashcards[0].front == "ما هو ML؟"

            fc_repo = FlashcardRepositoryImpl(db)
            from app.domain.entities.learning import (
                FlashcardReview,
            )

            fc_repo.save_review(
                FlashcardReview(
                    flashcard_id=flashcards[0].id,
                    rating="GOOD",
                )
            )
            reviews = (
                fc_repo.find_reviews_by_flashcard_id(
                    flashcards[0].id
                )
            )
            assert len(reviews) == 1
            assert reviews[0].rating == "GOOD"

    def test_fake_llm_provider(self):
        llm = FakeLLMProvider(response="test response")
        assert llm.is_available()
        assert llm.model_name == "fake-llm"
        assert llm.call_count == 0

        result = llm.generate("prompt")
        assert result == "test response"
        assert llm.call_count == 1

        llm.generate("prompt2")
        assert llm.call_count == 2

    def test_delete_all_learning_data(self, db):
        from app.domain.entities.learning import (
            LearningSummary,
            KeyConcept,
            Question,
            Flashcard,
        )

        summary_repo = LearningSummaryRepositoryImpl(db)
        concept_repo = KeyConceptRepositoryImpl(db)
        question_repo = QuestionRepositoryImpl(db)
        quiz_repo = QuizRepositoryImpl(db)
        fc_repo = FlashcardRepositoryImpl(db)

        summary_repo.save(
            LearningSummary(
                document_id="d1", title="S"
            )
        )
        concept_repo.save_many(
            [
                KeyConcept(
                    document_id="d1",
                    term="T",
                    definition="D",
                )
            ]
        )
        question_repo.save_many(
            [
                Question(
                    document_id="d1",
                    question="Q?",
                    answer="A",
                )
            ]
        )
        quiz = quiz_repo.save_quiz(
            Quiz(document_id="d1", title="Q")
        )
        quiz_repo.save_question(
            QuizQuestion(
                quiz_id=quiz.id,
                question="QQ?",
                correct_answer="A",
            )
        )
        fc_repo.save_many(
            [
                Flashcard(
                    document_id="d1",
                    front="F",
                    back="B",
                )
            ]
        )

        assert summary_repo.find_by_document_id("d1")
        assert concept_repo.find_by_document_id("d1")
        assert question_repo.find_by_document_id("d1")
        assert quiz_repo.find_quizzes_by_document_id(
            "d1"
        )
        assert fc_repo.find_by_document_id("d1")

        summary_repo.delete_by_document_id("d1")
        concept_repo.delete_by_document_id("d1")
        question_repo.delete_by_document_id("d1")
        quiz_repo.delete_quizzes_by_document_id("d1")
        fc_repo.delete_by_document_id("d1")

        assert (
            summary_repo.find_by_document_id("d1")
            is None
        )
        assert (
            len(concept_repo.find_by_document_id("d1"))
            == 0
        )
        assert (
            len(question_repo.find_by_document_id("d1"))
            == 0
        )
        assert (
            len(
                quiz_repo.find_quizzes_by_document_id(
                    "d1"
                )
            )
            == 0
        )
        assert (
            len(fc_repo.find_by_document_id("d1")) == 0
        )
