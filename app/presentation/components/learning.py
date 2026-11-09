"""Document-scoped learning session components."""

from __future__ import annotations

import logging

import streamlit as st

from app.presentation.components.common import friendly_error, source_citations

logger = logging.getLogger(__name__)


def render_learning_session(service, document_id: str) -> None:
    """Render the five learning steps for exactly one document."""
    stats = service.document_stats(document_id)
    completed = sum(
        (
            bool(stats.get("has_summary")),
            stats.get("concept_count", 0) > 0,
            stats.get("question_count", 0) > 0,
            stats.get("quiz_count", 0) > 0,
            stats.get("flashcard_count", 0) > 0,
        )
    )
    st.progress(completed / 5, text=f"اكتملت {completed} من 5 خطوات للتعلم")

    summary_tab, concepts_tab, questions_tab, quiz_tab, flashcards_tab = st.tabs(
        ["الفهم", "المفاهيم", "التدريب", "الاختبار", "المراجعة"]
    )
    with summary_tab:
        render_summary(service, document_id)
    with concepts_tab:
        render_concepts(service, document_id)
    with questions_tab:
        render_questions(service, document_id)
    with quiz_tab:
        render_quiz(service, document_id)
    with flashcards_tab:
        render_flashcards(service, document_id)


def _generate(action, success: str, failure: str) -> None:
    try:
        with st.spinner("يجري إنشاء المحتوى التعليمي…"):
            action()
        st.success(success, icon=":material/check_circle:")
        st.rerun()
    except Exception:
        logger.exception("Learning content generation failed")
        friendly_error(failure)


def render_summary(service, document_id: str) -> None:
    summary = service.summary_for(document_id)
    if summary is None:
        st.info("ابدأ بفهم المستند عبر ملخص موجز ومنظم.", icon=":material/article:")
        if st.button("إنشاء الملخص", type="primary", key=f"generate_summary_{document_id}", icon=":material/auto_awesome:"):
            _generate(lambda: service.generate_summary(document_id), "تم إنشاء الملخص.", "تعذر إنشاء الملخص حاليًا.")
        return

    st.subheader(summary.title)
    st.markdown(summary.overview)
    for section in summary.sections or []:
        if isinstance(section, dict):
            st.markdown(f"#### {section.get('title', '')}")
            st.markdown(section.get("content", ""))
        else:
            st.markdown(str(section))
    if summary.key_takeaways:
        st.markdown("#### أهم النقاط")
        for takeaway in summary.key_takeaways:
            st.markdown(f"- {takeaway}")
    source_citations(summary.sources or [])
    if st.button("إعادة إنشاء الملخص", key=f"regenerate_summary_{document_id}", icon=":material/refresh:"):
        service.delete_summary(document_id)
        st.rerun()


def render_concepts(service, document_id: str) -> None:
    concepts = service.concepts_for(document_id)
    if not concepts:
        st.info("استخرج المصطلحات والمفاهيم التي تحتاج إليها للمراجعة.", icon=":material/lightbulb:")
        if st.button("استخراج المفاهيم", type="primary", key=f"generate_concepts_{document_id}", icon=":material/auto_awesome:"):
            _generate(lambda: service.generate_concepts(document_id), "تم استخراج المفاهيم.", "تعذر استخراج المفاهيم حاليًا.")
        return

    for concept in concepts:
        with st.container(border=True):
            st.markdown(f"#### {concept.term}")
            st.markdown(f"**التعريف:** {concept.definition}")
            if concept.explanation:
                st.write(concept.explanation)
            if concept.importance:
                st.caption(f"الأهمية: {concept.importance}")
            if concept.topic:
                st.badge(concept.topic, icon=":material/label:", color="blue")
            source_citations(concept.sources or [])
    if st.button("إعادة استخراج المفاهيم", key=f"regenerate_concepts_{document_id}", icon=":material/refresh:"):
        service.delete_concepts(document_id)
        st.rerun()


def render_questions(service, document_id: str) -> None:
    questions = service.questions_for(document_id)
    if not questions:
        st.info("أنشئ أسئلة تدريبية لتتأكد من فهمك قبل الاختبار.", icon=":material/quiz:")
        if st.button("إنشاء أسئلة تدريبية", type="primary", key=f"generate_questions_{document_id}", icon=":material/auto_awesome:"):
            _generate(lambda: service.generate_questions(document_id), "تم إنشاء الأسئلة.", "تعذر إنشاء الأسئلة حاليًا.")
        return

    for index, question in enumerate(questions, 1):
        with st.container(border=True):
            st.markdown(f"**سؤال {index}:** {question.question}")
            with st.expander("عرض الإجابة", icon=":material/visibility:"):
                st.write(question.answer)
            difficulty = {"EASY": "سهل", "MEDIUM": "متوسط", "HARD": "متقدم"}.get(question.difficulty, question.difficulty)
            st.caption(f"الصعوبة: {difficulty}{f' · {question.topic}' if question.topic else ''}")
    if st.button("إعادة إنشاء الأسئلة", key=f"regenerate_questions_{document_id}", icon=":material/refresh:"):
        service.delete_questions(document_id)
        st.rerun()


def render_quiz(service, document_id: str) -> None:
    quiz, questions = service.quiz_for(document_id)
    if quiz is None:
        st.info("اختبر فهمك باختبار مستند إلى محتوى هذا المستند فقط.", icon=":material/fact_check:")
        if st.button("إنشاء اختبار", type="primary", key=f"generate_quiz_{document_id}", icon=":material/auto_awesome:"):
            _generate(lambda: service.generate_quiz(document_id), "تم إنشاء الاختبار.", "تعذر إنشاء الاختبار حاليًا.")
        return

    results_key = f"quiz_results_{document_id}"
    session_key = f"quiz_session_{document_id}"
    if results_key in st.session_state:
        _render_quiz_results(service, document_id, quiz)
    elif session_key in st.session_state:
        _render_active_quiz(service, document_id, quiz, questions)
    else:
        st.subheader(quiz.title)
        st.write(quiz.description)
        st.caption(f"عدد الأسئلة: {len(questions)}")
        if st.button("بدء الاختبار", type="primary", key=f"start_quiz_{document_id}", icon=":material/play_arrow:"):
            session = service.start_quiz(quiz.id)
            st.session_state[session_key] = session.id
            st.session_state[f"quiz_current_{document_id}"] = 0
            st.session_state[f"quiz_answers_{document_id}"] = {}
            st.rerun()


def _render_active_quiz(service, document_id: str, quiz, questions) -> None:
    current_key = f"quiz_current_{document_id}"
    answers_key = f"quiz_answers_{document_id}"
    current = st.session_state.get(current_key, 0)
    answers = st.session_state.get(answers_key, {})

    if current >= len(questions):
        if st.button("تسليم الاختبار", type="primary", key=f"submit_quiz_{document_id}", icon=":material/check_circle:"):
            answer_payload = [
                {"quiz_question_id": question_id, "user_answer": answer}
                for question_id, answer in answers.items()
            ]
            try:
                with st.spinner("يجري تصحيح الاختبار…"):
                    service.submit_quiz(st.session_state[f"quiz_session_{document_id}"], answer_payload)
                st.session_state[f"quiz_results_{document_id}"] = st.session_state[f"quiz_session_{document_id}"]
                st.session_state.pop(f"quiz_session_{document_id}", None)
                st.rerun()
            except Exception:
                logger.exception("Quiz submission failed")
                friendly_error("تعذر تصحيح الاختبار حاليًا.")
        return

    question = questions[current]
    st.progress((current + 1) / len(questions), text=f"السؤال {current + 1} من {len(questions)}")
    st.markdown(f"#### {question.question}")
    existing = answers.get(question.id)

    if question.question_type == "MCQ" and question.options:
        answer = st.radio("اختر الإجابة", question.options, index=(question.options.index(existing) if existing in question.options else 0), key=f"quiz_answer_{document_id}_{question.id}")
    elif question.question_type == "TRUE_FALSE":
        options = ["صحيح", "خاطئ"]
        answer = st.radio("اختر الإجابة", options, index=(options.index(existing) if existing in options else 0), key=f"quiz_answer_{document_id}_{question.id}")
    else:
        answer = st.text_input("اكتب إجابتك", value=existing or "", key=f"quiz_answer_{document_id}_{question.id}")

    with st.container(horizontal=True, horizontal_alignment="right"):
        if current > 0 and st.button("السابق", key=f"quiz_previous_{document_id}_{current}", icon=":material/arrow_forward:"):
            st.session_state[current_key] = current - 1
            st.rerun()
        if st.button("التالي", type="primary", key=f"quiz_next_{document_id}_{current}", icon=":material/arrow_back:"):
            answers[question.id] = answer
            st.session_state[answers_key] = answers
            st.session_state[current_key] = current + 1
            st.rerun()


def _render_quiz_results(service, document_id: str, quiz) -> None:
    session_id = st.session_state[f"quiz_results_{document_id}"]
    results = service.quiz_results(session_id)
    if not results:
        friendly_error("تعذر تحميل نتائج الاختبار.")
        return
    st.subheader("نتيجة الاختبار")
    metric_score, metric_percentage = st.columns(2)
    metric_score.metric("النتيجة", f"{results['score']} / {results['total']}")
    metric_percentage.metric("النسبة", f"{results['percentage']:.0f}%")
    for index, answer in enumerate(results.get("answers", []), 1):
        with st.container(border=True):
            label = "إجابة صحيحة" if answer.get("is_correct") else "تحتاج مراجعة"
            st.badge(label, icon=":material/check_circle:" if answer.get("is_correct") else ":material/error:", color="green" if answer.get("is_correct") else "red")
            st.markdown(f"**{index}. {answer.get('question', '')}**")
            if not answer.get("is_correct"):
                st.write(f"إجابتك: {answer.get('user_answer', '')}")
                st.write(f"الإجابة الصحيحة: {answer.get('correct_answer', '')}")
            if answer.get("explanation"):
                st.caption(answer["explanation"])
    if st.button("إعادة الاختبار", key=f"restart_quiz_{document_id}", icon=":material/replay:"):
        service.reset_quiz_sessions(quiz.id)
        for key in (f"quiz_results_{document_id}", f"quiz_current_{document_id}", f"quiz_answers_{document_id}"):
            st.session_state.pop(key, None)
        st.rerun()


def render_flashcards(service, document_id: str) -> None:
    flashcards = service.flashcards_for(document_id)
    if not flashcards:
        st.info("راجع أهم المعلومات باستخدام بطاقات مختصرة.", icon=":material/style:")
        if st.button("إنشاء بطاقات", type="primary", key=f"generate_flashcards_{document_id}", icon=":material/auto_awesome:"):
            _generate(lambda: service.generate_flashcards(document_id), "تم إنشاء البطاقات.", "تعذر إنشاء البطاقات حاليًا.")
        return

    index_key = f"flashcards_index_{document_id}"
    visible_key = f"flashcards_visible_{document_id}"
    ratings_key = f"flashcards_ratings_{document_id}"
    index = st.session_state.get(index_key, 0)
    ratings = st.session_state.setdefault(ratings_key, {})

    if index >= len(flashcards):
        known = sum(1 for rating in ratings.values() if rating in {"GOOD", "EASY"})
        st.success("أكملت مراجعة البطاقات.", icon=":material/check_circle:")
        st.metric("البطاقات المتقنة", f"{known} / {len(flashcards)}")
        if st.button("بدء مراجعة جديدة", key=f"restart_flashcards_{document_id}", icon=":material/replay:"):
            st.session_state[index_key] = 0
            st.session_state[visible_key] = False
            st.session_state[ratings_key] = {}
            st.rerun()
        return

    flashcard = flashcards[index]
    st.progress((index + 1) / len(flashcards), text=f"البطاقة {index + 1} من {len(flashcards)}")
    with st.container(border=True):
        st.markdown(f"#### {flashcard.front}")
        if not st.session_state.get(visible_key, False):
            if st.button("إظهار الإجابة", key=f"show_flashcard_{document_id}_{flashcard.id}", icon=":material/visibility:"):
                st.session_state[visible_key] = True
                st.rerun()
        else:
            st.markdown(f"**{flashcard.back}**")
            if flashcard.topic:
                st.caption(flashcard.topic)
            ratings = [("لم أعرف", "UNKNOWN"), ("صعب", "HARD"), ("جيد", "GOOD"), ("سهل", "EASY")]
            with st.container(horizontal=True, horizontal_alignment="distribute"):
                for label, rating in ratings:
                    if st.button(label, key=f"rate_flashcard_{document_id}_{flashcard.id}_{rating}"):
                        try:
                            service.review_flashcard(flashcard.id, rating)
                            st.session_state[ratings_key][flashcard.id] = rating
                            st.session_state[index_key] = index + 1
                            st.session_state[visible_key] = False
                            st.rerun()
                        except Exception:
                            logger.exception("Flashcard review failed")
                            friendly_error("تعذر حفظ مراجعة البطاقة.")
