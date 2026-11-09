"""Small, non-sensitive settings/status page."""

from __future__ import annotations

import streamlit as st

from app.config.settings import settings
from app.presentation.components.common import page_header


def render(service) -> None:
    page_header("الإعدادات", "راجع جاهزية المنصة قبل بدء التوليد أو المحادثة.")
    with st.container(border=True):
        st.subheader("حالة الخدمات")
        if settings.is_api_key_configured:
            st.success("خدمة الذكاء الاصطناعي مهيأة.", icon=":material/check_circle:")
        else:
            st.warning("خدمة الذكاء الاصطناعي غير مهيأة. يمكنك رفع المستندات، لكن إنشاء المحتوى والمحادثات لن تكون متاحة حتى إعداد المفتاح.", icon=":material/warning:")
        st.caption(f"نموذج اللغة: {settings.llm_model}")
        st.caption(f"نموذج التضمينات: {settings.embedding_model}")

    with st.container(border=True):
        st.subheader("تنظيم المستندات")
        st.write("المواد التنظيمية اختيارية، ويمكنك فتح أي مستند أو دراسته مباشرة من المكتبة.")
