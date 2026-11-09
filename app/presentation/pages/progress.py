"""Progress page with explicit, identifier-based scopes."""

from __future__ import annotations

import streamlit as st

from app.presentation.components.common import empty_state, page_header
from app.presentation.navigation.router import open_document


def render(service) -> None:
    page_header("التقدم", "تابع اكتمال رحلة التعلم، ثم اقرأ دقة الاختبارات كمؤشر منفصل.")
    documents = service.list_indexed_documents()
    if not documents:
        empty_state("لا يوجد تقدم بعد", "ارفع مستندًا وفهرسه ثم ابدأ جلسة التعلم.")
        return

    scopes = [("all", "كل المستندات")]
    scopes.extend((f"course:{course.id}", f"مادة: {course.name}") for course in service.list_courses())
    scopes.extend((f"document:{document.id}", f"مستند: {document.name}") for document in documents)
    labels = {key: label for key, label in scopes}

    active_id = st.session_state.get("active_document_id")
    default = f"document:{active_id}" if active_id and f"document:{active_id}" in labels else "all"
    selected_scope = st.selectbox(
        "نطاق العرض",
        options=list(labels),
        index=list(labels).index(default),
        format_func=lambda scope: labels[scope],
        key="progress_scope",
    )

    if selected_scope == "all":
        _render_global(service)
    elif selected_scope.startswith("course:"):
        _render_course(service, selected_scope.split(":", 1)[1])
    else:
        _render_document(service, selected_scope.split(":", 1)[1])


def _render_global(service) -> None:
    stats = service.global_stats()
    st.subheader("التقدم العام")
    st.progress(stats.overall_progress / 100, text=f"اكتمال رحلة التعلم: {stats.overall_progress:.0f}%")
    columns = st.columns(4)
    columns[0].metric("المستندات المفهرسة", stats.indexed_documents)
    columns[1].metric("الملخصات", stats.total_summaries)
    columns[2].metric("الاختبارات المكتملة", stats.total_quizzes)
    columns[3].metric("دقة الإجابات", f"{stats.accuracy:.0f}%")


def _render_course(service, course_id: str) -> None:
    stats = service.course_stats(course_id)
    if not stats:
        st.info("لا توجد مستندات ضمن هذه المادة.", icon=":material/info:")
        return
    course = next((item for item in service.list_courses() if item.id == course_id), None)
    st.subheader(f"تقدم المادة: {course.name if course else ''}")
    st.progress(stats["overall_progress"] / 100, text=f"اكتمال رحلة التعلم: {stats['overall_progress']:.0f}%")
    columns = st.columns(4)
    columns[0].metric("المستندات المفهرسة", stats["indexed_count"])
    columns[1].metric("الملخصات", stats["total_summaries"])
    columns[2].metric("الاختبارات المكتملة", stats["quiz_count"])
    columns[3].metric("دقة الإجابات", f"{stats['accuracy']:.0f}%")


def _render_document(service, document_id: str) -> None:
    stats = service.document_stats(document_id)
    if not stats:
        st.warning("هذا المستند غير متاح.", icon=":material/warning:")
        return
    document = stats["document"]
    completed = sum(
        (
            bool(stats["has_summary"]),
            stats["concept_count"] > 0,
            stats["question_count"] > 0,
            stats["quiz_count"] > 0,
            stats["flashcard_count"] > 0,
        )
    )
    st.subheader(f"تقدم المستند: {document.name}")
    st.progress(completed / 5, text=f"اكتملت {completed} من 5 خطوات للتعلم")
    columns = st.columns(4)
    columns[0].metric("المفاهيم", stats["concept_count"])
    columns[1].metric("الأسئلة", stats["question_count"])
    columns[2].metric("الاختبارات المكتملة", stats["quiz_count"])
    accuracy = stats["answers_correct"] / stats["answers_total"] * 100 if stats["answers_total"] else 0
    columns[3].metric("دقة الإجابات", f"{accuracy:.0f}%")
    if st.button("فتح مساحة المستند", key=f"progress_open_{document_id}", icon=":material/description:"):
        open_document(document_id)
