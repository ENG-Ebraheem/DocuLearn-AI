"""Separate general-AI and document-grounded chat experiences."""

from __future__ import annotations

import logging

import streamlit as st

from app.presentation.components.common import empty_state, friendly_error, page_header, source_citations
from app.presentation.navigation.router import navigate, open_document
from app.presentation.state.session_state import PAGE_LIBRARY

logger = logging.getLogger(__name__)


def render(service) -> None:
    page_header("المحادثة", "اختر بين الذكاء الاصطناعي العام والمحادثة المستندة إلى مستند محدد.")
    general_tab, document_tab = st.tabs(["الذكاء الاصطناعي العام", "محادثة مستند"])
    with general_tab:
        render_general_chat(service)
    with document_tab:
        _render_document_chat_entry(service)


def render_general_chat(service) -> None:
    st.info("🤖 الذكاء الاصطناعي العام: هذه المحادثة تمنحك إجابات عامة ومستقلة عن المستندات ولا تستخدم مصادر مكتبتك.", icon=":material/smart_toy:")
    messages = st.session_state.setdefault("general_chat_messages", [])

    pending = st.session_state.pop("pending_general_question", None)
    if pending:
        _answer_general_question(service, pending)
        st.rerun()

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("اسأل الذكاء الاصطناعي عن أي موضوع", key="general_chat_input", submit_mode="disable")
    if prompt:
        _answer_general_question(service, prompt)
        st.rerun()


def _answer_general_question(service, prompt: str) -> None:
    messages = st.session_state.setdefault("general_chat_messages", [])
    messages.append({"role": "user", "content": prompt})
    history = [{"role": message["role"], "content": message["content"]} for message in messages[:-1]]
    try:
        with st.spinner("يجري إعداد الإجابة…"):
            response = service.answer_general_question(prompt, history)
        messages.append({"role": "assistant", "content": response.answer})
    except Exception:
        logger.exception("General chat failed")
        messages.append({"role": "assistant", "content": "تعذر إنشاء الإجابة الآن. حاول مرة أخرى."})


def _render_document_chat_entry(service) -> None:
    documents = service.list_indexed_documents()
    if not documents:
        empty_state(
            "لا توجد مستندات مفهرسة",
            "ارفع مستندًا وفهرسه من المكتبة قبل بدء محادثة مستند.",
            "فتح مكتبتي",
            lambda: navigate(PAGE_LIBRARY, remember_current_page=False),
        )
        return

    active_id = st.session_state.get("active_document_id")
    mapping = {document.id: document for document in documents}
    selected_id = st.selectbox(
        "المستند",
        options=list(mapping),
        index=list(mapping).index(active_id) if active_id in mapping else 0,
        format_func=lambda document_id: mapping[document_id].name,
        key="chat_document_selector",
    )
    if selected_id != active_id:
        st.session_state["active_document_id"] = selected_id
    render_document_chat(service, selected_id)


def render_document_chat(service, document_id: str) -> None:
    document = service.get_document(document_id)
    if document is None or document.status != "INDEXED":
        st.warning("اختر مستندًا مفهرسًا لبدء المحادثة.", icon=":material/warning:")
        return

    st.caption(f"📄 محادثة المستند: تبحث هذه المحادثة في «{document.name}» فقط، وتعرض مصادر الإجابة.")
    conversation, messages = service.document_messages(document_id)
    for message in messages:
        with st.chat_message(message.role):
            st.markdown(message.content)
            source_citations(message.sources or [])

    fallback_key = f"document_fallback_{document_id}"
    fallback = st.session_state.get(fallback_key)
    if fallback:
        st.warning("لا توجد معلومات كافية في هذا المستند للإجابة عن هذا السؤال.", icon=":material/find_in_page:")
        if st.button("🤖 اسأل General AI", type="primary", key=f"fallback_to_general_{document_id}", icon=":material/open_in_new:"):
            st.session_state["pending_general_question"] = fallback["query"]
            st.session_state.pop(fallback_key, None)
            navigate("chat", remember_current_page=True)
        if st.button("إلغاء", key=f"cancel_document_fallback_{document_id}"):
            st.session_state.pop(fallback_key, None)
            st.rerun()

    prompt = st.chat_input(
        f"اسأل عن محتوى «{document.name}»",
        key=f"document_chat_input_{document_id}",
        submit_mode="disable",
    )
    if not prompt:
        return

    service.save_document_message(conversation.id, "user", prompt)
    history = [{"role": message.role, "content": message.content} for message in messages]
    try:
        with st.spinner("يجري البحث في المستند…"):
            response = service.answer_document_question(prompt, document_id, history)
    except Exception:
        logger.exception("Document chat failed")
        friendly_error("تعذر البحث في المستند الآن. حاول مرة أخرى.")
        return

    if not response.has_sufficient_context:
        st.session_state[fallback_key] = {"query": prompt, "history": history}
    else:
        sources = [
            {
                "document_id": source.document_id,
                "document_name": source.document_name,
                "page": source.page,
                "chunk_id": source.chunk_id,
                "score": source.score,
                "excerpt": source.excerpt,
            }
            for source in response.sources
        ]
        service.save_document_message(conversation.id, "assistant", response.answer, sources)
    st.rerun()
