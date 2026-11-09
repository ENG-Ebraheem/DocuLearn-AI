"""Analytics page with explicit document or course scope."""

from __future__ import annotations

import streamlit as st

from app.presentation.components.common import empty_state, page_header


def render(service) -> None:
    page_header("التحليلات", "اقرأ أداءك ضمن نطاق واضح، ثم استخدم النتائج لتحديد ما يحتاج إلى مراجعة.")
    documents = service.list_indexed_documents()
    if not documents:
        empty_state("لا توجد تحليلات بعد", "تظهر التحليلات بعد فهرسة مستند والبدء في التدريب أو الاختبارات.")
        return

    scopes = [("all", "كل المستندات")]
    scopes.extend((f"course:{course.id}", f"مادة: {course.name}") for course in service.list_courses())
    scopes.extend((f"document:{document.id}", f"مستند: {document.name}") for document in documents)
    labels = dict(scopes)
    active_id = st.session_state.get("active_document_id")
    default = f"document:{active_id}" if active_id and f"document:{active_id}" in labels else "all"
    selected = st.selectbox(
        "نطاق التحليلات",
        options=list(labels),
        index=list(labels).index(default),
        format_func=lambda scope: labels[scope],
        key="analytics_scope",
    )

    if selected == "all":
        _render_global(service)
    elif selected.startswith("course:"):
        _render_course(service, selected.split(":", 1)[1])
    else:
        _render_document(service, selected.split(":", 1)[1])


def _render_global(service) -> None:
    stats = service.global_stats()
    columns = st.columns(4)
    columns[0].metric("إجمالي الإجابات", stats.total_answers)
    columns[1].metric("الإجابات الصحيحة", stats.correct_answers)
    columns[2].metric("دقة الاختبارات", f"{stats.accuracy:.0f}%")
    columns[3].metric("مراجعات البطاقات", stats.total_flashcard_reviews)
    _render_topic_performance(stats.strong_topics, stats.weak_topics)


def _render_course(service, course_id: str) -> None:
    stats = service.course_stats(course_id)
    if not stats:
        st.info("لا توجد مستندات ضمن هذه المادة.", icon=":material/info:")
        return
    columns = st.columns(4)
    columns[0].metric("إجمالي الإجابات", stats["answers_total"])
    columns[1].metric("الإجابات الصحيحة", stats["answers_correct"])
    columns[2].metric("دقة الاختبارات", f"{stats['accuracy']:.0f}%")
    columns[3].metric("البطاقات المتقنة", stats["flashcards_known"])
    st.caption("تحليلات الموضوعات التفصيلية متاحة عند اختيار مستند محدد.")


def _render_document(service, document_id: str) -> None:
    stats = service.document_stats(document_id)
    if not stats:
        st.warning("هذا المستند غير متاح.", icon=":material/warning:")
        return
    columns = st.columns(4)
    columns[0].metric("الأسئلة التدريبية", stats["question_count"])
    columns[1].metric("إجمالي الإجابات", stats["answers_total"])
    columns[2].metric("الإجابات الصحيحة", stats["answers_correct"])
    accuracy = stats["answers_correct"] / stats["answers_total"] * 100 if stats["answers_total"] else 0
    columns[3].metric("دقة الاختبارات", f"{accuracy:.0f}%")
    topics = service.document_topics(document_id)
    st.subheader("موضوعات المستند")
    if not topics:
        st.caption("ستظهر الموضوعات بعد إنشاء أسئلة أو بطاقات لهذا المستند.")
        return
    for topic, values in topics.items():
        with st.container(border=True):
            st.markdown(f"**{topic}**")
            st.caption(f"{values.get('question_count', 0)} سؤال تدريبي")


def _render_topic_performance(strong_topics, weak_topics) -> None:
    strong_column, weak_column = st.columns(2)
    with strong_column:
        st.subheader("نقاط القوة")
        if strong_topics:
            for topic in strong_topics[:5]:
                st.success(f"{topic.topic} — {topic.accuracy:.0f}%", icon=":material/thumb_up:")
        else:
            st.caption("لا توجد بيانات كافية بعد.")
    with weak_column:
        st.subheader("يحتاج إلى مراجعة")
        if weak_topics:
            for topic in weak_topics[:5]:
                st.warning(f"{topic.topic} — {topic.accuracy:.0f}%", icon=":material/replay:")
        else:
            st.caption("لا توجد موضوعات تحتاج إلى مراجعة حاليًا.")
