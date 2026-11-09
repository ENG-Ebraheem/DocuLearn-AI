"""Dashboard page: concise learning overview, not a data dump."""

from __future__ import annotations

import streamlit as st

from app.presentation.components.common import empty_state, page_header
from app.presentation.components.document_card import render_document_card
from app.presentation.navigation.router import navigate, open_document
from app.presentation.state.session_state import PAGE_LIBRARY, PAGE_STUDY


def render(service) -> None:
    page_header("مرحبًا بك في DocuLearn AI", "ارفَع مستندًا، افهمه، ثم تعلّم منه خطوة بخطوة.")
    stats = service.global_stats()
    documents = service.list_documents()

    if not documents:
        empty_state(
            "لا توجد مستندات بعد",
            "ابدأ برفع أول مستند لتتمكن من الدردشة والدراسة والاختبار من محتواه.",
            "فتح مكتبتي",
            lambda: navigate(PAGE_LIBRARY, remember_current_page=False),
        )
        return

    metrics = st.columns(3)
    metrics[0].metric("المستندات", stats.total_documents)
    metrics[1].metric("المستندات المفهرسة", stats.indexed_documents)
    metrics[2].metric("التقدم العام", f"{stats.overall_progress:.0f}%")

    active_id = st.session_state.get("active_document_id")
    last_opened_id = st.session_state.get("last_opened_document_id")
    active_document = service.get_document(active_id) if active_id else None
    last_opened_document = service.get_document(last_opened_id) if last_opened_id else None
    indexed_documents = [doc for doc in documents if doc.status == "INDEXED"]
    continue_document = (
        last_opened_document
        if last_opened_document and last_opened_document.status == "INDEXED"
        else active_document
        if active_document and active_document.status == "INDEXED"
        else indexed_documents[0]
        if indexed_documents
        else None
    )

    if continue_document:
        st.subheader("تابع التعلّم")
        with st.container(border=True):
            st.markdown(f"#### {continue_document.name}")
            document_stats = service.document_stats(continue_document.id)
            completed = sum(
                (
                    bool(document_stats.get("has_summary")),
                    document_stats.get("concept_count", 0) > 0,
                    document_stats.get("question_count", 0) > 0,
                    document_stats.get("quiz_count", 0) > 0,
                    document_stats.get("flashcard_count", 0) > 0,
                )
            )
            st.progress(completed / 5, text=f"اكتملت {completed} من 5 خطوات للتعلم")
            with st.container(horizontal=True, horizontal_alignment="right"):
                if st.button("متابعة الدراسة", type="primary", key="dashboard_continue_study", icon=":material/play_arrow:"):
                    navigate(PAGE_STUDY, document_id=continue_document.id)
                if st.button("فتح المستند", key="dashboard_open_document", icon=":material/description:"):
                    open_document(continue_document.id)

    st.subheader("مستندات حديثة")
    recent = sorted(documents, key=lambda doc: doc.created_at, reverse=True)[:3]
    for document in recent:
        render_document_card(service, document, key_prefix="dashboard")

    st.subheader("إجراءات سريعة")
    with st.container(horizontal=True, horizontal_alignment="right"):
        if st.button("فتح مكتبتي", key="dashboard_library", icon=":material/library_books:"):
            navigate(PAGE_LIBRARY, remember_current_page=False)
        if st.button("بدء الدراسة", key="dashboard_study", icon=":material/school:"):
            navigate(PAGE_STUDY, remember_current_page=False)
