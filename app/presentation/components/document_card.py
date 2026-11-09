"""Document list and workspace header components."""

from __future__ import annotations

import streamlit as st

from app.presentation.components.common import status_badge
from app.presentation.navigation.router import navigate, open_document
from app.presentation.state.session_state import PAGE_STUDY


def render_document_card(service, document, *, key_prefix: str = "document") -> None:
    stats = service.document_stats(document.id)
    with st.container(border=True):
        st.markdown(f"#### {document.name}")
        metadata = f"{document.file_type.upper()} · {document.pages or '—'} صفحة"
        if stats:
            metadata += f" · {stats.get('chunks', 0)} أجزاء"
        st.caption(metadata)
        status_badge(document.status)

        with st.container(horizontal=True, horizontal_alignment="right"):
            if document.status == "INDEXED":
                if st.button("فتح", key=f"{key_prefix}_open_{document.id}", icon=":material/description:"):
                    open_document(document.id)
                if st.button("دراسة", key=f"{key_prefix}_study_{document.id}", icon=":material/school:"):
                    navigate(PAGE_STUDY, document_id=document.id)
                if st.button("محادثة", key=f"{key_prefix}_chat_{document.id}", icon=":material/chat:"):
                    open_document(document.id, section="chat")
            else:
                st.caption("أكمل المعالجة قبل فتح المستند.")


def render_document_context(service, document_id: str) -> object | None:
    document = service.get_document(document_id)
    if document is None:
        return None
    stats = service.document_stats(document_id)
    chunks_count = stats.get("chunks", 0) if stats else 0
    with st.container(border=True):
        st.markdown(f"### 📄 {document.name}")
        st.caption(f"{document.file_type.upper()} · {document.pages or '—'} صفحة · {chunks_count} أجزاء مفهرسة")
        status_badge(document.status)
    return document
