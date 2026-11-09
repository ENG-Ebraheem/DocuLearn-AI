"""Reusable native Streamlit presentation components."""

from __future__ import annotations

import streamlit as st


STATUS_LABELS = {
    "INDEXED": "مفهرس",
    "PROCESSING": "قيد المعالجة",
    "FAILED": "تعذرت المعالجة",
    "UPLOADED": "مرفوع",
    "NEEDS_OCR": "يحتاج معالجة نصية",
}
STATUS_COLORS = {
    "INDEXED": "green",
    "PROCESSING": "orange",
    "FAILED": "red",
    "UPLOADED": "blue",
    "NEEDS_OCR": "orange",
}


def page_header(title: str, description: str | None = None, icon: str | None = None) -> None:
    st.title(title, text_alignment="right")
    if description:
        st.caption(description, text_alignment="right")


def empty_state(title: str, description: str, action_label: str | None = None, action=None) -> None:
    with st.container(border=True):
        st.subheader(title)
        st.write(description)
        if action_label and action and st.button(action_label, type="primary", key=f"empty_{action_label}"):
            action()


def status_badge(status: str) -> None:
    st.badge(
        STATUS_LABELS.get(status, status),
        icon=":material/check_circle:" if status == "INDEXED" else ":material/schedule:",
        color=STATUS_COLORS.get(status, "blue"),
    )


def source_citations(sources: list) -> None:
    if not sources:
        return
    with st.expander("المصادر", icon=":material/attach_file:"):
        for index, source in enumerate(sources, 1):
            page = source.get("page") if isinstance(source, dict) else source.page
            name = source.get("document_name", "") if isinstance(source, dict) else source.document_name
            excerpt = source.get("excerpt", "") if isinstance(source, dict) else source.excerpt
            page_text = f" — الصفحة {page}" if page else ""
            st.markdown(f"**{index}. {name}**{page_text}")
            if excerpt:
                st.caption(excerpt)


def friendly_error(message: str = "حدث خطأ أثناء تنفيذ العملية. حاول مرة أخرى.") -> None:
    st.error(message, icon=":material/error:")
