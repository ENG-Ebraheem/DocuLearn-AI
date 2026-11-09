"""تنقل واجهة DocuLearn AI مع الحفاظ على السياق."""

from __future__ import annotations

import streamlit as st

from app.presentation.state.session_state import (
    NAVIGATION_PAGES,
    PAGE_ANALYTICS,
    PAGE_CHAT,
    PAGE_DASHBOARD,
    PAGE_DOCUMENT,
    PAGE_LIBRARY,
    PAGE_PROGRESS,
    PAGE_SETTINGS,
    PAGE_STUDY,
    set_active_document,
)


PAGE_LABELS = {
    PAGE_DASHBOARD: "الرئيسية",
    PAGE_LIBRARY: "ملفاتي",
    PAGE_STUDY: "وضع التعلم",
    PAGE_CHAT: "المحادثة",
    PAGE_PROGRESS: "التقدم",
    PAGE_ANALYTICS: "التحليلات",
    PAGE_SETTINGS: "الإعدادات",
}


def navigate(
    page: str,
    *,
    document_id: str | None = None,
    course_id: str | None = None,
    section: str | None = None,
    remember_current_page: bool = True,
) -> None:
    """Navigate once, retaining the meaningful page to which Back should return."""
    if page not in NAVIGATION_PAGES and page != PAGE_DOCUMENT:
        raise ValueError(f"Unknown page: {page}")

    current_page = st.session_state.get("current_page", PAGE_LIBRARY)
    if remember_current_page and page == PAGE_DOCUMENT and current_page != PAGE_DOCUMENT:
        st.session_state["return_page"] = current_page

    if document_id is not None:
        set_active_document(document_id)
    if course_id is not None:
        st.session_state["active_course_id"] = course_id
    if section is not None:
        st.session_state["active_section"] = section

    st.session_state["current_page"] = page
    st.rerun()


def back_to_context() -> None:
    """Return from a document-scoped view to the page from which it was opened."""
    destination = st.session_state.get("return_page", PAGE_LIBRARY)
    if destination == PAGE_DOCUMENT:
        destination = PAGE_LIBRARY
    st.session_state["current_page"] = destination
    st.rerun()


def get_back_label() -> str:
    """Return context-aware back button title."""
    destination = st.session_state.get("return_page", PAGE_LIBRARY)
    if destination == PAGE_DOCUMENT:
        destination = PAGE_LIBRARY
    label = PAGE_LABELS.get(destination, "ملفاتي")
    return f"العودة إلى {label}"


def open_document(document_id: str, section: str = "chat") -> None:
    navigate(PAGE_DOCUMENT, document_id=document_id, section=section)


def open_course(course_id: str) -> None:
    st.session_state["active_course_id"] = course_id
    navigate(PAGE_LIBRARY, remember_current_page=False)


