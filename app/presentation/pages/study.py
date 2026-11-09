"""Document-scoped study page."""

from __future__ import annotations

import streamlit as st

from app.presentation.components.common import empty_state, page_header
from app.presentation.components.document_card import render_document_context
from app.presentation.components.learning import render_learning_session
from app.presentation.navigation.router import back_to_context, navigate
from app.presentation.state.session_state import PAGE_LIBRARY


def render(service) -> None:
    page_header("جلسة التعلم", "اختر مستندًا أولًا، ثم افهمه وتدرّب عليه واختبر نفسك.")
    document_id = st.session_state.get("active_document_id")
    document = service.get_document(document_id) if document_id else None

    if document is None or document.status != "INDEXED":
        _render_selector(service)
        return

    render_document_context(service, document.id)
    if st.button("تغيير المستند", key="study_change_document", icon=":material/swap_horiz:"):
        st.session_state["active_document_id"] = None
        st.rerun()
    render_learning_session(service, document.id)


def _render_selector(service) -> None:
    documents = service.list_indexed_documents()
    if not documents:
        empty_state(
            "لا توجد مستندات جاهزة للتعلم",
            "ارفع مستندًا وفهرسه من المكتبة قبل بدء جلسة التعلم.",
            "فتح مكتبتي",
            lambda: navigate(PAGE_LIBRARY, remember_current_page=False),
        )
        return

    st.subheader("اختر مستندًا للدراسة")
    st.caption("ستبقى كل خطوات التعلم والاختبار والمراجعة مرتبطة بهذا المستند فقط.")

    courses = service.list_courses()
    course_options = {"كل المواد": None, **{course.name: course.id for course in courses}}
    selected_course_label = st.selectbox("المادة (اختياري)", list(course_options), key="study_course_filter")
    selected_course_id = course_options[selected_course_label]

    filtered_docs = (
        [doc for doc in documents if doc.course_id == selected_course_id]
        if selected_course_id
        else documents
    )

    if not filtered_docs:
        st.info("لا توجد مستندات مفهرسة تحت هذه المادة.", icon=":material/info:")
        return

    mapping = {doc.id: doc for doc in filtered_docs}
    selected_id = st.selectbox(
        "المستند",
        options=list(mapping),
        format_func=lambda doc_id: mapping[doc_id].name,
        key="study_document_selector",
    )
    selected = mapping[selected_id]
    with st.container(border=True):
        st.markdown(f"#### {selected.name}")
        st.caption(f"{selected.file_type.upper()} · {selected.pages or '—'} صفحة")
        if st.button("ابدأ جلسة التعلم", type="primary", key=f"start_study_{selected.id}", icon=":material/play_arrow:"):
            st.session_state["active_document_id"] = selected.id
            st.rerun()
