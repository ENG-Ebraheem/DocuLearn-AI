"""DocuLearn AI Streamlit entry point."""

from __future__ import annotations

import logging

import streamlit as st

from app.bootstrap import create_platform_service
from app.presentation.components.common import friendly_error
from app.presentation.components.sidebar import render_sidebar
from app.presentation.pages import analytics, dashboard, document, library, progress, settings, study
from app.presentation.pages import chat as chat_page
from app.presentation.state.session_state import (
    PAGE_ANALYTICS,
    PAGE_CHAT,
    PAGE_DASHBOARD,
    PAGE_DOCUMENT,
    PAGE_LIBRARY,
    PAGE_PROGRESS,
    PAGE_SETTINGS,
    PAGE_STUDY,
    initialize_session_state,
)
from app.presentation.styles.theme import apply_theme

logger = logging.getLogger(__name__)

PAGE_RENDERERS = {
    PAGE_DASHBOARD: dashboard.render,
    PAGE_LIBRARY: library.render,
    PAGE_DOCUMENT: document.render,
    PAGE_STUDY: study.render,
    PAGE_CHAT: chat_page.render,
    PAGE_PROGRESS: progress.render,
    PAGE_ANALYTICS: analytics.render,
    PAGE_SETTINGS: settings.render,
}


def main() -> None:
    st.set_page_config(
        page_title="DocuLearn AI",
        page_icon=":material/school:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()
    initialize_session_state()

    service = None
    try:
        service = create_platform_service()
        render_sidebar(service)
        current_page = st.session_state.get("current_page", PAGE_DASHBOARD)
        renderer = PAGE_RENDERERS.get(current_page, dashboard.render)
        renderer(service)
    except Exception:
        logger.exception("Unexpected application error")
        friendly_error("حدث خطأ أثناء تحميل التطبيق. أعد المحاولة، وإذا استمر الخطأ فتحقق من إعدادات الخدمة.")
    finally:
        if service is not None:
            service.close()


if __name__ == "__main__":
    main()