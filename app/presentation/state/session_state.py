"""حالة جلسة موحدة خاصة بواجهة DocuLearn AI."""

from __future__ import annotations

import streamlit as st

PAGE_DASHBOARD = "dashboard"
PAGE_LIBRARY = "library"
PAGE_DOCUMENT = "document"
PAGE_STUDY = "study"
PAGE_CHAT = "chat"
PAGE_PROGRESS = "progress"
PAGE_ANALYTICS = "analytics"
PAGE_SETTINGS = "settings"

NAVIGATION_PAGES = (
    PAGE_DASHBOARD,
    PAGE_LIBRARY,
    PAGE_STUDY,
    PAGE_CHAT,
    PAGE_PROGRESS,
    PAGE_ANALYTICS,
    PAGE_SETTINGS,
)


def initialize_session_state() -> None:
    """Initialize all cross-page state in one predictable location."""
    defaults = {
        "current_page": PAGE_DASHBOARD,
        "return_page": PAGE_LIBRARY,
        "active_document_id": None,
        "last_opened_document_id": None,
        "active_course_id": None,
        "active_section": "chat",
        "chat_mode": "general",
        "general_chat_messages": [],
        "pending_general_question": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def set_active_document(document_id: str | None) -> None:
    st.session_state["active_document_id"] = document_id
    if document_id is not None:
        st.session_state["last_opened_document_id"] = document_id
    _reset_document_ephemeral_state()


def clear_active_document_if_matches(document_id: str) -> None:
    if st.session_state.get("active_document_id") == document_id:
        set_active_document(None)
        st.session_state["current_page"] = PAGE_LIBRARY


def _reset_document_ephemeral_state() -> None:
    """Clear only temporary state whose validity depends on the active document."""
    for key in list(st.session_state.keys()):
        if key.startswith(("document_fallback_", "quiz_", "flashcards_")):
            st.session_state.pop(key, None)


def document_scoped_key(name: str, document_id: str) -> str:
    return f"{name}_{document_id}"
