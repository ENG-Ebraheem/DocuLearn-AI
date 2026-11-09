"""Application shell sidebar."""

from __future__ import annotations

import streamlit as st

from app.presentation.navigation.router import navigate, open_document
from app.presentation.state.session_state import (
    PAGE_ANALYTICS,
    PAGE_CHAT,
    PAGE_DASHBOARD,
    PAGE_LIBRARY,
    PAGE_PROGRESS,
    PAGE_SETTINGS,
    PAGE_STUDY,
)

NAV_ITEMS = (
    (PAGE_DASHBOARD, "الرئيسية", ":material/home:"),
    (PAGE_LIBRARY, "مكتبتي", ":material/library_books:"),
    (PAGE_STUDY, "التعلم", ":material/school:"),
    (PAGE_CHAT, "المحادثة", ":material/chat:"),
    (PAGE_PROGRESS, "التقدم", ":material/trending_up:"),
    (PAGE_ANALYTICS, "التحليلات", ":material/analytics:"),
    (PAGE_SETTINGS, "الإعدادات", ":material/settings:"),
)


def render_sidebar(service) -> None:
    """Render compact, consistent app navigation and active-document context."""
    with st.sidebar:
        st.markdown("## DocuLearn AI")
        st.caption("تعلّم من مستنداتك بوضوح")

        current_page = st.session_state.get("current_page", PAGE_DASHBOARD)
        for page, label, icon in NAV_ITEMS:
            if st.button(
                label,
                key=f"nav_{page}",
                icon=icon,
                type="primary" if page == current_page else "secondary",
                width="stretch",
            ):
                navigate(page, remember_current_page=False)

        st.divider()
        st.caption("المستند النشط")
        document_id = st.session_state.get("active_document_id")
        document = service.get_document(document_id) if document_id else None
        if document is None:
            st.caption("لم تحدد مستندًا بعد.")
        else:
            st.markdown(f"**{document.name}**")
            st.caption(f"{document.file_type.upper()} · {document.pages or '—'} صفحة")
            if st.button("فتح المستند", key="sidebar_open_document", icon=":material/description:", width="stretch"):
                open_document(document.id)
