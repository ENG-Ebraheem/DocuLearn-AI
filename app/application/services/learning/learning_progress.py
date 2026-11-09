from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TopicPerformance:
    topic: str = ""
    total_answers: int = 0
    correct_answers: int = 0
    accuracy: float = 0.0
    flashcards_reviewed: int = 0
    flashcards_known: int = 0


@dataclass
class LearningStats:
    total_documents: int = 0
    indexed_documents: int = 0
    total_questions: int = 0
    total_quizzes: int = 0
    total_answers: int = 0
    correct_answers: int = 0
    accuracy: float = 0.0
    total_flashcards: int = 0
    total_flashcard_reviews: int = 0
    flashcards_known: int = 0
    total_summaries: int = 0
    total_concepts: int = 0
    overall_progress: float = 0.0
    strong_topics: list = field(default_factory=list)
    weak_topics: list = field(default_factory=list)
    topic_performances: dict = field(
        default_factory=dict
    )
    recent_activity: list = field(default_factory=list)


class LearningProgressService:

    def __init__(
        self,
        doc_repo,
        chunk_repo,
        summary_repo,
        concept_repo,
        question_repo,
        quiz_repo,
        flashcard_repo,
        topic_repo,
    ):
        self.doc_repo = doc_repo
        self.chunk_repo = chunk_repo
        self.summary_repo = summary_repo
        self.concept_repo = concept_repo
        self.question_repo = question_repo
        self.quiz_repo = quiz_repo
        self.flashcard_repo = flashcard_repo
        self.topic_repo = topic_repo

    def get_stats(self) -> LearningStats:
        docs = self.doc_repo.find_all()
        indexed_docs = [
            d for d in docs if d.status == "INDEXED"
        ]

        questions = self.question_repo.find_all()
        summaries = self.summary_repo.find_all()
        concepts = self.concept_repo.find_all()
        flashcards = self.flashcard_repo.find_all()

        completed_sessions = (
            self.quiz_repo.find_completed_sessions()
        )
        all_answers = (
            self.quiz_repo.find_all_answers()
        )
        all_reviews = (
            self.flashcard_repo.find_all_reviews()
        )

        total_answers = len(all_answers)
        correct_answers = sum(
            1 for a in all_answers if a.is_correct
        )
        accuracy = (
            (correct_answers / total_answers * 100)
            if total_answers > 0
            else 0.0
        )

        flashcards_known = sum(
            1
            for r in all_reviews
            if r.rating in ("GOOD", "EASY")
        )

        overall_progress = self._compute_progress(
            doc_count=len(indexed_docs),
            summary_count=len(summaries),
            concept_count=len(concepts),
            question_count=len(questions),
            quiz_count=len(completed_sessions),
            answer_count=total_answers,
            flashcard_count=len(flashcards),
            review_count=len(all_reviews),
        )

        topic_perfs = self._compute_topic_performance(
            all_answers, all_reviews, flashcards
        )

        strong = sorted(
            [
                t
                for t in topic_perfs.values()
                if t.total_answers >= 1
                and t.accuracy >= 70.0
            ],
            key=lambda t: t.accuracy,
            reverse=True,
        )

        weak = sorted(
            [
                t
                for t in topic_perfs.values()
                if t.total_answers >= 1
                and t.accuracy < 70.0
            ],
            key=lambda t: t.accuracy,
        )

        activity = self._build_recent_activity(
            docs,
            completed_sessions,
            all_reviews,
            summaries,
        )

        return LearningStats(
            total_documents=len(docs),
            indexed_documents=len(indexed_docs),
            total_questions=len(questions),
            total_quizzes=len(completed_sessions),
            total_answers=total_answers,
            correct_answers=correct_answers,
            accuracy=accuracy,
            total_flashcards=len(flashcards),
            total_flashcard_reviews=len(all_reviews),
            flashcards_known=flashcards_known,
            total_summaries=len(summaries),
            total_concepts=len(concepts),
            overall_progress=overall_progress,
            strong_topics=strong,
            weak_topics=weak,
            topic_performances=topic_perfs,
            recent_activity=activity,
        )

    def get_document_stats(
        self, document_id: str
    ) -> dict:
        doc = self.doc_repo.find_by_id(document_id)
        if doc is None:
            return {}

        chunks = self.chunk_repo.find_by_document_id(
            document_id
        )
        summary = self.summary_repo.find_by_document_id(
            document_id
        )
        concepts = self.concept_repo.find_by_document_id(
            document_id
        )
        questions = self.question_repo.find_by_document_id(
            document_id
        )
        quizzes = (
            self.quiz_repo.find_quizzes_by_document_id(
                document_id
            )
        )
        flashcards = (
            self.flashcard_repo.find_by_document_id(
                document_id
            )
        )

        quiz_ids = {q.id for q in quizzes}

        quiz_question_ids = set()
        quiz_id_to_question_ids = {}
        for qid in quiz_ids:
            qs = self.quiz_repo.find_questions_by_quiz_id(
                qid
            )
            qids = [qq.id for qq in qs]
            quiz_id_to_question_ids[qid] = qids
            quiz_question_ids.update(qids)

        all_answers = self.quiz_repo.find_all_answers()
        total_answers = 0
        correct_answers = 0
        session_count = 0

        all_sessions = (
            self.quiz_repo.find_all_sessions()
        )
        doc_session_ids = set()
        for s in all_sessions:
            if s.quiz_id in quiz_ids:
                doc_session_ids.add(s.id)
                if s.status == "completed":
                    session_count += 1

        for ans in all_answers:
            if ans.session_id in doc_session_ids:
                total_answers += 1
                if ans.is_correct:
                    correct_answers += 1

        fc_ids = [fc.id for fc in flashcards]
        reviews = (
            self.flashcard_repo.find_reviews_by_flashcard_ids(
                fc_ids
            )
        )
        fc_known = sum(
            1
            for r in reviews
            if r.rating in ("GOOD", "EASY")
        )

        return {
            "document": doc,
            "chunks": len(chunks),
            "has_summary": summary is not None,
            "concept_count": len(concepts),
            "question_count": len(questions),
            "quiz_count": session_count,
            "flashcard_count": len(flashcards),
            "answers_total": total_answers,
            "answers_correct": correct_answers,
            "flashcards_known": fc_known,
            "flashcards_reviewed": len(reviews),
        }

    def get_document_topics(
        self, document_id: str
    ) -> dict:
        questions = self.question_repo.find_by_document_id(
            document_id
        )
        topics = {}
        for q in questions:
            topic = q.topic or "عام"
            if topic not in topics:
                topics[topic] = {
                    "topic": topic,
                    "question_count": 0,
                }
            topics[topic]["question_count"] += 1

        flashcards = (
            self.flashcard_repo.find_by_document_id(
                document_id
            )
        )
        for fc in flashcards:
            topic = fc.topic or "عام"
            if topic not in topics:
                topics[topic] = {
                    "topic": topic,
                    "question_count": 0,
                }

        return topics

    def _compute_progress(
        self,
        doc_count,
        summary_count,
        concept_count,
        question_count,
        quiz_count,
        answer_count,
        flashcard_count,
        review_count,
    ) -> float:
        if doc_count == 0:
            return 0.0

        weights = {
            "summary": 20.0,
            "concepts": 15.0,
            "questions": 15.0,
            "quizzes": 20.0,
            "flashcards": 15.0,
            "reviews": 15.0,
        }

        summary_score = min(
            summary_count / max(doc_count, 1), 1.0
        )
        concept_score = min(
            concept_count / max(doc_count * 5, 1), 1.0
        )
        question_score = min(
            question_count / max(doc_count * 5, 1), 1.0
        )
        quiz_score = min(
            quiz_count / max(doc_count, 1), 1.0
        )
        flashcard_score = min(
            flashcard_count / max(doc_count * 5, 1),
            1.0,
        )
        review_score = min(
            review_count / max(flashcard_count, 1),
            1.0,
        )

        total = (
            summary_score * weights["summary"]
            + concept_score * weights["concepts"]
            + question_score * weights["questions"]
            + quiz_score * weights["quizzes"]
            + flashcard_score * weights["flashcards"]
            + review_score * weights["reviews"]
        )

        return round(total, 1)

    def _compute_topic_performance(
        self,
        all_answers,
        all_reviews,
        all_flashcards,
    ) -> dict:
        topic_map: dict[str, TopicPerformance] = {}

        all_sessions = (
            self.quiz_repo.find_all_sessions()
        )
        session_quiz_map = {}
        for s in all_sessions:
            session_quiz_map[s.id] = s.quiz_id

        question_cache: dict[str, dict] = {}
        for ans in all_answers:
            quiz_id = session_quiz_map.get(
                ans.session_id, ""
            )
            if quiz_id not in question_cache:
                qs = (
                    self.quiz_repo.find_questions_by_quiz_id(
                        quiz_id
                    )
                )
                question_cache[quiz_id] = {
                    q.id: q for q in qs
                }

            q_map = question_cache[quiz_id]
            question = q_map.get(ans.quiz_question_id)
            topic = (
                question.topic
                if question and question.topic
                else "عام"
            )

            if topic not in topic_map:
                topic_map[topic] = TopicPerformance(
                    topic=topic
                )

            topic_map[topic].total_answers += 1
            if ans.is_correct:
                topic_map[topic].correct_answers += 1

        for tp in topic_map.values():
            if tp.total_answers > 0:
                tp.accuracy = round(
                    tp.correct_answers
                    / tp.total_answers
                    * 100,
                    1,
                )

        fc_topic_map = {}
        for fc in all_flashcards:
            fc_topic_map[fc.id] = (
                fc.topic or "عام"
            )

        for review in all_reviews:
            topic = fc_topic_map.get(
                review.flashcard_id, "عام"
            )
            if topic not in topic_map:
                topic_map[topic] = TopicPerformance(
                    topic=topic
                )
            topic_map[
                topic
            ].flashcards_reviewed += 1
            if review.rating in ("GOOD", "EASY"):
                topic_map[
                    topic
                ].flashcards_known += 1

        return topic_map

    def _build_recent_activity(
        self,
        docs,
        sessions,
        reviews,
        summaries,
    ) -> list[dict]:
        activity = []

        for doc in docs[-5:]:
            activity.append(
                {
                    "type": "document",
                    "label": f"تمت إضافة المستند '{doc.name}'",
                    "date": doc.created_at,
                }
            )

        for s in sessions[-5:]:
            activity.append(
                {
                    "type": "quiz",
                    "label": f"اختبار مكتمل - نتيجة: {s.percentage:.0f}%",
                    "date": s.completed_at
                    or s.started_at,
                }
            )

        for r in reviews[-5:]:
            activity.append(
                {
                    "type": "flashcard",
                    "label": f"بطاقة مُراجعة - {r.rating}",
                    "date": r.reviewed_at,
                }
            )

        for s in summaries[-5:]:
            activity.append(
                {
                    "type": "summary",
                    "label": f"ملخص مُنشأ - '{s.title}'",
                    "date": s.created_at,
                }
            )

        activity.sort(
            key=lambda a: (
                a["date"]
                if a["date"]
                else datetime.min.replace(
                    tzinfo=timezone.utc
                )
            ),
            reverse=True,
        )

        return activity[:10]

    def get_course_stats(
        self, course_id: str
    ) -> dict:
        documents = self.doc_repo.find_by_course_id(
            course_id
        )
        if not documents:
            return {}

        doc_ids = [d.id for d in documents]
        indexed = [
            d for d in documents if d.status == "INDEXED"
        ]

        all_answers = self.quiz_repo.find_all_answers()
        all_sessions = (
            self.quiz_repo.find_all_sessions()
        )

        doc_quiz_ids = set()
        for doc in indexed:
            quizzes = (
                self.quiz_repo.find_quizzes_by_document_id(
                    doc.id
                )
            )
            for q in quizzes:
                doc_quiz_ids.add(q.id)

        doc_session_ids = set()
        session_count = 0
        for s in all_sessions:
            if s.quiz_id in doc_quiz_ids:
                doc_session_ids.add(s.id)
                if s.status == "completed":
                    session_count += 1

        total_answers = 0
        correct_answers = 0
        for ans in all_answers:
            if ans.session_id in doc_session_ids:
                total_answers += 1
                if ans.is_correct:
                    correct_answers += 1

        accuracy = (
            (correct_answers / total_answers * 100)
            if total_answers > 0
            else 0.0
        )

        total_summaries = 0
        total_concepts = 0
        total_questions = 0
        total_flashcards = 0
        for doc_id in doc_ids:
            s = self.summary_repo.find_by_document_id(
                doc_id
            )
            if s:
                total_summaries += 1
            total_concepts += len(
                self.concept_repo.find_by_document_id(
                    doc_id
                )
            )
            total_questions += len(
                self.question_repo.find_by_document_id(
                    doc_id
                )
            )
            total_flashcards += len(
                self.flashcard_repo.find_by_document_id(
                    doc_id
                )
            )

        all_reviews = (
            self.flashcard_repo.find_all_reviews()
        )
        doc_fc_ids = set()
        for doc_id in doc_ids:
            fcs = (
                self.flashcard_repo.find_by_document_id(
                    doc_id
                )
            )
            for fc in fcs:
                doc_fc_ids.add(fc.id)

        doc_reviews = [
            r
            for r in all_reviews
            if r.flashcard_id in doc_fc_ids
        ]
        fc_known = sum(
            1
            for r in doc_reviews
            if r.rating in ("GOOD", "EASY")
        )

        progress = self._compute_progress(
            doc_count=len(indexed),
            summary_count=total_summaries,
            concept_count=total_concepts,
            question_count=total_questions,
            quiz_count=session_count,
            answer_count=total_answers,
            flashcard_count=total_flashcards,
            review_count=len(doc_reviews),
        )

        return {
            "documents": documents,
            "document_count": len(documents),
            "indexed_count": len(indexed),
            "total_summaries": total_summaries,
            "total_concepts": total_concepts,
            "total_questions": total_questions,
            "total_flashcards": total_flashcards,
            "quiz_count": session_count,
            "answers_total": total_answers,
            "answers_correct": correct_answers,
            "accuracy": accuracy,
            "flashcards_reviewed": len(doc_reviews),
            "flashcards_known": fc_known,
            "overall_progress": progress,
        }
