"""Document workspace page."""

from __future__ import annotations

import streamlit as st

from app.presentation.components.common import empty_state, page_header
from app.presentation.components.document_card import render_document_context
from app.presentation.components.learning import (
    render_concepts,
    render_flashcards,
    render_questions,
    render_quiz,
    render_summary,
)


from app.presentation.navigation.router import back_to_context, get_back_label, navigate
from app.presentation.pages.chat import render_document_chat
from app.presentation.state.session_state import PAGE_LIBRARY


def render(service) -> None:
    document_id = st.session_state.get("active_document_id")
    if not document_id:
        empty_state(
            "اختر مستندًا أولًا",
            "افتح مستندًا من مكتبتك لبدء المحادثة أو جلسة التعلم.",
            "فتح مكتبتي",
            lambda: navigate(PAGE_LIBRARY, remember_current_page=False),
        )
        return

    document = render_document_context(service, document_id)
    if document is None:
        st.session_state["active_document_id"] = None
        empty_state(
            "لم يعد هذا المستند متاحًا",
            "ربما حُذف المستند في جلسة سابقة. اختر مستندًا آخر من مكتبتك.",
            "فتح مكتبتي",
            lambda: navigate(PAGE_LIBRARY, remember_current_page=False),
        )
        return

    with st.container(horizontal=True, horizontal_alignment="right"):
        if st.button(get_back_label(), key="document_back", icon=":material/arrow_forward:"):
            back_to_context()

    workspace_tabs = st.tabs(
        ["💬 المحادثة", "📖 الملخص", "🧠 المفاهيم", "❓ الأسئلة", "📝 الاختبار", "🃏 البطاقات"]
    )
    with workspace_tabs[0]:
        render_document_chat(service, document_id)
    with workspace_tabs[1]:
        render_summary(service, document_id)
    with workspace_tabs[2]:
        render_concepts(service, document_id)
    with workspace_tabs[3]:
        render_questions(service, document_id)
    with workspace_tabs[4]:
        render_quiz(service, document_id)
    with workspace_tabs[5]:
        render_flashcards(service, document_id)

